
##############################################################################
##
# This file is part of Sardana
##
# http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

# NOTE!!!
# This controller is based on icepap API 3
# https://github.com/ALBA-Synchrotron/pyIcePAP

import time
import numpy
from icepap import IcePAPController
from PyTango import AttributeProxy
from sardana import State, DataAccess
from sardana.pool.controller import MotorController, Type, Access, \
    Description, DefaultValue, MaxDimSize


ReadOnly = DataAccess.ReadOnly
ReadWrite = DataAccess.ReadWrite


class IcepapController(MotorController):
    """
    This class is the Sardana motor controller for the ICEPAP motor controller.
    Appart from the standard Pool motor interface per axis, it provides extra
    attributes for some firmware attributes of the driver.
    """

    # The properties used to connect to the IcePAP motor controller
    ctrl_properties = {
        'Host': {Type: str, Description: 'The host name'},
        'Port': {Type: int, Description: 'The port number',
                 DefaultValue: 5000},
        'Timeout': {Type: int, Description: 'Connection timeout',
                    DefaultValue: 3},
        'IcepapLogLevel': {Type: str,
                           Description: 'Icepap library logging level',
                           DefaultValue: 'INFO'},
        'DefaultAutoESYNC': {Type: bool,
                             Description: 'Default value for '
                                          'AutoESYNC attribute',
                             DefaultValue: False},
    }

    ctrl_attributes = {
        'Pmux': {
            Type: str,
            Description: 'Attribute to set/get the PMUX configuration. '
                         'Multiple comma separated commands are allowed as set value. '
                         'See IcePAP user manual pag. 107',
            Access: DataAccess.ReadWrite},
    }
    axis_attributes = {
        'MoveInGroup': {Type: bool, Access: ReadWrite,
                        Description: 'Attribute to set the group flag '
                                     'on the movement',
                        DefaultValue: True},
        'AutoESYNC': {Type: bool, Access: ReadWrite,
                      Description: 'Attribute to send ESYNC command before '
                                   'to do the absolute position calculation.'},

        'Indexer': {Type: str, Access: ReadWrite},
        'PowerOn': {Type: bool, Access: ReadWrite},
        'InfoA': {Type: str, Access: ReadWrite},
        'InfoB': {Type: str, Access: ReadWrite},
        'InfoC': {Type: str, Access: ReadWrite},
        'EnableEncoder_5V': {Type: bool, Access: ReadWrite},
        'ClosedLoop': {Type: bool, Access: ReadWrite},
        'PosAxis': {Type: float, Access: ReadOnly},
        # TODO: Check because in fw 3.17 does not work
        # 'PosIndexer': {Type: float, Access: ReadOnly},
        'PosShftEnc': {Type: float, Access: ReadOnly},
        'PosTgtEnc': {Type: float, Access: ReadOnly},
        'PosEncIn': {Type: float, Access: ReadOnly},
        'PosInPos': {Type: float, Access: ReadOnly},
        'PosAbsEnc': {Type: float, Access: ReadOnly},
        'PosMotor': {Type: float, Access: ReadOnly},
        'VelMotor': {Type: float, Access: ReadOnly},
        'VelCurrent': {Type: float, Access: ReadOnly},
        'DifAxTgtEnc': {Type: float, Access: ReadOnly},
        'DifAxShftEnc': {Type: float, Access: ReadOnly},
        'DifAxMotor': {Type: float, Access: ReadOnly},
        'EncAxis': {Type: float, Access: ReadOnly},
        # TODO: Check because in fw 3.17 does not work
        # 'EncIndexer': {Type: float, Access: ReadOnly},
        'EncShftEnc': {Type: float, Access: ReadOnly},
        'EncTgtEnc': {Type: float, Access: ReadOnly},
        'EncEncIn': {Type: float, Access: ReadOnly},
        'EncInPos': {Type: float, Access: ReadOnly},
        'EncAbsEnc': {Type: float, Access: ReadOnly},
        'MeasureI': {Type: float, Access: ReadOnly},
        # 12/08/2009 REQUESTED FROM LOTHAR, A COMPLETE MESSAGE ABOUT WHAT
        # IS HAPPENING
        'StatusDriverBoard': {Type: int, Access: ReadOnly},
        # 12/08/2009 GOOD TO KNOW WHAT IS REALLY HAPPENING TO THE AXIS
        # POWER STATE
        'PowerInfo': {Type: str, Access: ReadOnly},
        'MotorEnabled': {Type: bool, Access: ReadWrite},
        'Status5vpower': {Type: bool, Access: ReadOnly},
        'StatusAlive': {Type: bool, Access: ReadOnly},
        'StatusCode': {Type: int, Access: ReadOnly},
        'StatusPowerOn': {Type: bool, Access: ReadOnly},
        'StatusDisable': {Type: bool, Access: ReadOnly},
        'StatusHome': {Type: bool, Access: ReadOnly},
        'StatusIndexer': {Type: str, Access: ReadOnly},
        'StatusInfo': {Type: int, Access: ReadOnly},
        'StatusLimPos': {Type: bool, Access: ReadOnly},
        'StatusLimNeg': {Type: bool, Access: ReadOnly},
        'StatusLim+': {Type: bool, Access: ReadOnly},
        'StatusLim-': {Type: bool, Access: ReadOnly},
        'StatusMode': {Type: str, Access: ReadOnly},
        'StatusMoving': {Type: bool, Access: ReadOnly},
        'StatusOutOfWin': {Type: bool, Access: ReadOnly},
        'StatusPresent': {Type: bool, Access: ReadOnly},
        'StatusReady': {Type: bool, Access: ReadOnly},
        'StatusSettling': {Type: bool, Access: ReadOnly},
        'StatusStopCode': {Type: str, Access: ReadOnly},
        'StatusStopCodeValue': {Type: int, Access: ReadOnly},
        'StatusVersErr': {Type: bool, Access: ReadOnly},
        'StatusWarning': {Type: bool, Access: ReadOnly},
        'StatusDetails': {Type: str, Access: ReadOnly},
        'UseEncoderSource': {Type: bool, Access: ReadWrite},
        'EncoderSource': {Type: str, Access: ReadWrite},
        'EncoderSourceFormula': {Type: str, Access: ReadWrite},
        'Encoder': {Type: float, Access: ReadOnly},
        'EcamDatTable': {Type: [float], Access: ReadWrite,
                         MaxDimSize: (20477,)},
        'SyncAux': {Type: str,
                    Description: 'Internal auxiliary synchronization line. '
                                 'It can use the same signals sources than '
                                 'InfoX.',
                    Access: ReadWrite},
        'SyncPos': {Type: str,
                    Description: 'Associates the internal Sync signal to the '
                                 'position signal selected',
                    Access: ReadWrite},
        'SyncRes': {Type: str,
                    Description: 'Sets the resolution of the internal Sync '
                                 'position signal.',
                    Access: ReadWrite},
        'EcamOut': {Type: str,
                    Description: 'Ecam signal output [OFF, PULSE, LOW, HIGH]',
                    Access: ReadWrite},
    }

    gender = "Motor"
    model = "Icepap"
    organization = "ALBA"
    image = "icepaphw.png"
    logo = "icepap.png"
    icon = "icepapicon.png"
    state = ""
    status = ""

    MaxDevice = 128

    def __init__(self, inst, props, *args, **kwargs):
        """ Do the default init plus the icepap connection
        @param inst instance name of the controller
        @param properties of the controller
        """
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.ipap = IcePAPController(self.Host, self.Port, self.Timeout,
                                     auto_axes=True)
        self.attributes = {}
        self.state_multiple = []
        self.position_multiple = []
        self.move_multiple_grouped = []
        self.move_multiple_not_grouped = []
        self.stop_multiple = []
        self.abort_multiple = []

        # Set IcePAP library logging level
        import logging
        logger = logging.getLogger('icepap')
        logger.setLevel(self.IcepapLogLevel)
        self._log.debug('Icepap logging level set to %s' % self.IcepapLogLevel)

    def AddDevice(self, axis):
        """ Set default values for the axis and try to connect to it
        @param axis to be added
        """

        self.attributes[axis] = {}
        self.attributes[axis]['step_per_unit'] = 1
        self.attributes[axis]['step_per_unit_set'] = False
        self.attributes[axis]['velocity'] = None
        self.attributes[axis]['status_value'] = None
        self.attributes[axis]['last_state_value'] = None
        self.attributes[axis]['position_value'] = None
        self.attributes[axis]['motor_enabled'] = True
        self.attributes[axis]['use_encoder_source'] = False
        self.attributes[axis]['encoder_source'] = 'attr://PosEncIn'
        self.attributes[axis]['encoder_source_formula'] = 'VALUE/SPU'
        self.attributes[axis]['encoder_source_tango_attribute'] = \
            FakedAttributeProxy(self, axis, 'attr://PosEncIn')
        self.attributes[axis]['internal_encoder'] = True
        self.attributes[axis]['move_in_group'] = True
        self.attributes[axis]['auto_esync'] = self.DefaultAutoESYNC


        if axis in self.ipap:
            self._log.info('Added axis %d.' % axis)
        else:
            self.attributes[axis]['motor_enabled'] = False
            self._log.warning('Added axis %d BUT NOT ALIVE -> '
                              'MotorEnabled set to False.' % axis)

    def DeleteDevice(self, axis):
        """ Nothing special to do. """
        self.attributes.pop(axis)

    def PreStateAll(self):
        """ If there is no connection, to the Icepap system, return False"""
        self.state_multiple = []

    def PreStateOne(self, axis):
        """ Store all positions in a variable and then react on the StateAll
        method.
        @param axis to get state
        """
        if self.attributes[axis]['motor_enabled'] is True:
            self.state_multiple.append(axis)
            self.attributes[axis]['status_value'] = None

    def StateAll(self):
        """
        Get State of all axis with just one command to the Icepap Controller.
        """
        try:
            ans = self.ipap.get_states(self.state_multiple)
            for axis, state in zip(self.state_multiple, ans):
                self.attributes[axis]['status_value'] = state
        except Exception as e:
            self._log.error('StateAll(%s) Hint: some driver board not '
                            'present?.\nException:\n%s' %
                            (str(self.state_multiple), str(e)))

    def StateOne(self, axis):
        """
        Connect to the hardware and check the state. If no connection
        available, return ALARM.
        @param axis to read the state
        @return the state value: {ALARM|ON|MOVING}
        """

        name = self.GetAxisName(axis)
        if axis not in self.state_multiple:

            self._log.warning('StateOne(%s(%s)) Not enabled. Check the Driver '
                              'Board is present in %s.', name, axis, self.Host)
            self.attributes[axis]["last_state_value"] = State.Alarm
            return State.Fault, 'Motor Not Enabled or Not Present', \
                self.NoLimitSwitch

        status_template = "STATE({0}) PWR({1}) RDY({2}) MOVING({3}) " \
                          "SETTLING({4}) STPCODE({5}) LIM+({6}) LIM-({7})"

        axis_state = self.attributes[axis]['status_value']

        if axis_state is None:
            self.attributes[axis]["last_state_value"] = State.Alarm
            return State.Alarm, 'Status Register not available', \
                self.NoLimitSwitch

        moving_flags = [axis_state.is_moving(), axis_state.is_settling()]
        alarm_flags = [axis_state.is_limit_positive(),
                       axis_state.is_limit_negative(),
                       not axis_state.is_poweron()]

        if any(moving_flags):
            state = State.Moving
            status_state = 'Moving'
        elif any(alarm_flags):
            state = State.Alarm
            status_state = 'Alarm'
        else:
            state = State.On
            status_state = 'On'
        status = status_template.format(status_state,
                                        axis_state.is_poweron(),
                                        axis_state.is_ready(),
                                        axis_state.is_moving(),
                                        axis_state.is_settling(),
                                        axis_state.get_stop_str(),
                                        axis_state.is_limit_positive(),
                                        axis_state.is_limit_negative())

        switchstate = self.NoLimitSwitch
        if axis_state.is_limit_negative():
            switchstate |= self.LowerLimitSwitch
        if axis_state.is_limit_positive():
            switchstate |= self.UpperLimitSwitch

        # TODO: Analyze this code
        # previous_state = self.attributes[axis]["last_state_value"]
        # if previous_state != State.Alarm and state == State.Alarm:
        #     dump = self.ipap.debug_internals(axis)
        #     self._log.warning('StateOne(%s(%s)).State change from %s '
        #                       'to %s. Icepap internals dump:\n%s',
        #                       name, axis, previous_state,
        #                       State[state], dump)
        self.attributes[axis]["last_state_value"] = state

        return state, status, switchstate

    def PreReadAll(self):
        """ If there is no connection, to the Icepap system, return False"""
        self.position_multiple = []

    def PreReadOne(self, axis):
        self.attributes[axis]["position_value"] = None
        # THERE IS AN IMPROVEMENT HERE, WE COULD GROUP ALL THE AXIS WHICH HAVE
        # A COMMON TANGO DEVICE IN THE POSITION SOURCE AND QUERY ALL AT ONCE
        # THE ATTRIBUTES RELATED TO THOSE AXIS OF COURSE THIS MEANS THAT
        # ReadAll HAS ALSO TO BE REIMPLEMENTED AND self.positionMultiple HAS
        # TO BE SPLITTED IN ORDER TO QUERY SOME AXIS TO ICEPAP
        # SOME OTHERS TO ONE DEVICE, SOME OTHERS TO ANOTHER DEVICE, ETC....
        motor_enabled = self.attributes[axis]['motor_enabled']
        use_encoder_source = self.attributes[axis]['use_encoder_source']
        if motor_enabled and not use_encoder_source:
            self.position_multiple.append(axis)
        elif not motor_enabled:
            self._log.debug('PreReadOne: driver board %s not present.' % axis)

    def ReadAll(self):
        """ We connect to the Icepap system for each axis. """
        try:
            if len(self.position_multiple) != 0:
                ans = self.ipap.get_pos(self.position_multiple)
                for axis, position in zip(self.position_multiple, ans):
                    self.attributes[axis]['position_value'] = float(position)
        except Exception as e:
            self._log.error('ReadAll(%s) Hint: some driver board not '
                            'present?.\nException:\n%s' %
                            (str(self.position_multiple), str(e)))

    def ReadOne(self, axis):
        """ Read the position of the axis.
        @param axis to read the position
        @return the current axis position
        """
        name = self.GetAxisName(axis)
        log = self._log
        if axis not in self.position_multiple:
            # IN CASE OF EXTERNAL SOURCE, JUST READ IT AND EVALUATE THE FORMULA
            if self.attributes[axis]['use_encoder_source']:
                try:
                    return self.getEncoder(axis)
                except Exception as e:
                    log.error('ReadOne (%s): Error %s' % (axis, repr(e)))
                    raise
            else:
                log.warning('ReadOne(%s(%d)) Not enabled. Check the Driver '
                            'Board is present in %s.', name, axis, self.Host)
                raise Exception('ReadOne(%s(%d)) Not enabled: No position '
                                'value available' % (name, axis))

        try:
            spu = self.attributes[axis]["step_per_unit"]
            pos = self.attributes[axis]['position_value']
            return pos / spu
        except Exception:
            log.error('ReadOne(%s(%d)) Exception:', name, axis, exc_info=1)
            raise

    def PreStartAll(self):
        """ If there is no connection, to the Icepap system, return False"""
        self.move_multiple_grouped = []
        self.move_multiple_not_grouped = []

    def StartOne(self, axis, pos):
        """ Store all positions in a variable and then react on the StartAll
                method.
                @param axis to start
                @param pos to move to
                """

        spu = self.attributes[axis]["step_per_unit"]
        # The desired absolute position based on the theoretical position
        # register (Axis/Motor). The reading of the position depends of
        # Axis configuration. If the closed loop is ON the encoder
        # position is near to the theoretical (set position), it depends of
        # closed loop configuration.
        # This controller allows to use an external encoder source like a
        # ADC card or another internal axis register as absolute position
        # value for Sardana. The theoretical position can differ
        # to the measured one, this generates some different errors on the
        # movements, to avoid it the controller sends the ESYNC command,
        # when the axis has the attribute UseEncoderSource set to True.

        if not self.attributes[axis]['use_encoder_source']:

            desired_absolute_steps_pos = pos * spu

        else:
            if self.attributes[axis]['internal_encoder'] and \
                    self.attributes[axis]['auto_esync']:
                try:
                    self.ipap[axis].esync()
                except Exception as e:
                    self._log.error('StartOne(%d,%f).\nException:\n%s' %
                                    (axis, pos, str(e)))
                    return False

            try:
                current_source_pos = self.getEncoder(axis)
                current_steps_pos = self.ipap[axis].pos
            except Exception as e:
                self._log.error('StartOne(%d,%f).\nException:\n%s' %
                                (axis, pos, str(e)))
                return False
            pos_increment = pos - current_source_pos
            steps_increment = pos_increment * spu
            desired_absolute_steps_pos = current_steps_pos + steps_increment

        if self.attributes[axis]['move_in_group']:
            self.move_multiple_grouped.append((axis,
                                               desired_absolute_steps_pos))
        else:
            self.move_multiple_not_grouped.append((axis,
                                                   desired_absolute_steps_pos))

        return True

    def StartAll(self):
        """ Move all axis at all position with just one command to the Icepap
        Controller. """
        # Optimize the synchronization in case of have one motor in the
        # group mode.
        move_not_grouped = len(self.move_multiple_not_grouped) != 0
        if len(self.move_multiple_grouped) == 1 and move_not_grouped:
            self.move_multiple_not_grouped.append(
                self.move_multiple_grouped.pop())

        if len(self.move_multiple_grouped) > 0:
            try:
                self.ipap.move(self.move_multiple_grouped)
                self._log.info('moveMultiple: '
                               + str(self.move_multiple_grouped))
            except Exception as e:
                self._log.error('StartAll(%s).\nException:\n%s' %
                                (str(self.move_multiple_grouped), str(e)))
                raise

        if len(self.move_multiple_not_grouped) > 0:
            try:
                self.ipap.move(self.move_multiple_not_grouped, group=False)
                self._log.info('moveMultiple not grouped: '
                               + str(self.move_multiple_not_grouped))
            except Exception as e:
                self._log.error('StartAll(%s).\nException:\n%s' %
                                (str(self.move_multiple_grouped), str(e)))
                axes_grouped = []
                for axis, _ in self.move_multiple_grouped:
                    axes_grouped.append(axis)
                if len(axes_grouped) > 0:
                    self.ipap.stop(axes_grouped)

                raise

    def PreStopAll(self):
        self.stop_multiple = []
        self.abort_multiple = []

    def StopOne(self, axis):
        # not sure about that, it comes from AbortOne implementation
        # due to the IcePAP firmware bug:
        # axes with velocity to acceleration time factor less that 18
        # are not stoppable
        try:
            factor = self.ipap[axis].velocity / self.ipap[axis].acctime
        except Exception as e:
            msg = 'Problems while trying to determine velocity to ' + \
                  'acceleration factor'
            self._log.error('StopOne(%d): %s. Trying to abort...' %
                            (axis, msg))
            self._log.debug(e)
            self.AbortOne(axis)
            raise Exception(msg)
        if factor < 18:
            self.AbortOne(axis)
        else:
            self.stop_multiple.append(axis)

    def StopAll(self):
        self.ipap.stop(self.stop_multiple)
        time.sleep(0.05)
        if len(self.abort_multiple) > 0:
            self.AbortAll()

    def PreAbortAll(self):
        self.abort_multiple = []

    def AbortOne(self, axis):
        self.abort_multiple.append(axis)

    def AbortAll(self):
        self.ipap.abort(self.abort_multiple)
        time.sleep(0.05)

    def DefinePosition(self, axis, position):
        step_pos = position * self.attributes[axis]['step_per_unit']
        self.ipap[axis].pos = step_pos

    def _SetVelocity(self, axis, velocity_steps):
        # setting the velocity changes the icepap acceleration time
        # for protection. We compensate this by restoring the
        # acceleration time back to the original value after
        # setting the new velocity
        accel_time = self.ipap[axis].acctime
        self.ipap[axis].velocity = velocity_steps
        self.ipap[axis].acctime = accel_time

    def SetAxisPar(self, axis, name, value):
        """ Set the standard pool motor parameters.
        @param axis to set the parameter
        @param name of the parameter
        @param value to be set
        """

        par_name = name.lower()
        if par_name == 'step_per_unit':
            self.attributes[axis]['step_per_unit_set'] = True
            spu = float(value)
            self.attributes[axis]['step_per_unit'] = spu
            velocity = self.attributes[axis]['velocity']
            if velocity is not None:
                self._SetVelocity(axis, velocity * spu)
        elif par_name == 'velocity':
            self.attributes[axis]['velocity'] = value
            spu = self.attributes[axis]['step_per_unit']
            if not self.attributes[axis]['step_per_unit_set']:
                # if step_per_unit has not been set yet we still try to
                # set velocity because the motor may simply use the default 
                # step per unit of 1. If it fails we ignore the error. The
                # velocity will be set when the step per unit is configured
                try:
                    self._SetVelocity(axis, value * spu)
                except:
                    pass
            else:
                self._SetVelocity(axis, value * spu)
        elif par_name == 'base_rate':
            pass
        elif par_name == 'acceleration':
            self.ipap[axis].acctime = value
        elif par_name == 'deceleration':
            pass
        else:
            MotorController.SetAxisPar(self, axis, name, value)

    def GetAxisPar(self, axis, name):
        """ Get the standard pool motor parameters.
        @param axis to get the parameter
        @param name of the parameter to get the value
        @return the value of the parameter
        """
        par_name = name.lower()
        if par_name == 'step_per_unit':
            value = self.attributes[axis]['step_per_unit']
        elif par_name == 'velocity':
            spu = self.attributes[axis]['step_per_unit']
            value = self.ipap[axis].velocity / spu
        elif par_name == 'base_rate':
            value = 0
        elif par_name in ['acceleration', 'deceleration']:
            value = self.ipap[axis].acctime
        else:
            value = MotorController.GetAxisPar(self, axis, name)
        return value

    # -------------------------------------------------------------------------
    #               Axis Extra Parameters
    # -------------------------------------------------------------------------
    def getMoveInGroup(self, axis):
        return self.attributes[axis]['move_in_group']

    def setMoveInGroup(self, axis, value):
        self.attributes[axis]['move_in_group'] = value

    def getAutoESYNC(self, axis):
        return self.attributes[axis]['auto_esync']

    def setAutoESYNC(self, axis, value):
        self.attributes[axis]['auto_esync'] = value

    def getPowerInfo(self, axis):
        # TODO: Analyze if it is included on the lib.
        return '\n'.join(self.ipap[axis].send_cmd('?ISG ?PWRINFO'))

    def getMotorEnabled(self, axis):
        return self.attributes[axis]['motor_enabled']

    def setMotorEnabled(self, axis, value):
        self.attributes[axis]['motor_enabled'] = value

    def getUseEncoderSource(self, axis):
        return self.attributes[axis]['use_encoder_source']

    def setUseEncoderSource(self, axis, value):
        self.attributes[axis]['use_encoder_source'] = value

    def getEncoderSource(self, axis):
        return self.attributes[axis]['encoder_source']

    def setEncoderSource(self, axis, value):
        self.attributes[axis]['encoder_source'] = value
        self.attributes[axis]['encoder_source_tango_attribute'] = None
        if value == '':
            return
        try:
            # check if it is an internal attribute
            enc_src_name = 'encoder_source_tango_attribute'
            if value.lower().startswith('attr://'):
                self.attributes[axis]['internal_encoder'] = True
                # 2012/03/27 Improve attr:// syntax to
                # allow reading of other axis of the same
                # system without
                # having to access them via tango://
                value_contents = value[7:]
                if ':' not in value_contents:
                    self.attributes[axis][enc_src_name] = \
                        FakedAttributeProxy(self, axis, value)
                else:
                    other_axis, other_value = \
                        value_contents.split(':')
                    other_axis = int(other_axis)
                    other_value = 'attr://' + other_value
                    self.attributes[axis][enc_src_name] = \
                        FakedAttributeProxy(self, other_axis, other_value)
            else:
                self.attributes[axis]['internal_encoder'] = False
                self.attributes[axis][enc_src_name] = \
                    AttributeProxy(value)
        except Exception as e:
            self._log.error('SetAxisExtraPar(%d,%s).\nException:\n%s' %
                            (axis, 'EncoderSource', str(e)))
            self.attributes[axis]['use_encoder_source'] = False

    def getEncoderSourceFormula(self, axis):
        return self.attributes[axis]['encoder_source_formula']

    def setEncoderSourceFormula(self, axis, value):
        self.attributes[axis]['encoder_source_formula'] = value

    def getEncoder(self, axis):
        try:
            enc_src_tango_attr = self.attributes[axis][
                'encoder_source_tango_attribute']
            if enc_src_tango_attr is not None:
                value = float(enc_src_tango_attr.read().value)
                eval_globals = numpy.__dict__
                spu = float(self.attributes[axis]['step_per_unit'])
                eval_locals = {'VALUE': value, 'value': value,
                               'SPU': spu, 'spu': spu}
                enc_src_formula = self.attributes[axis][
                    'encoder_source_formula']
                current_source_pos = eval(enc_src_formula,
                                          eval_globals,
                                          eval_locals)
                return float(current_source_pos)
            else:
                return float('NaN')
        except Exception as e:
            msg = 'Encoder(%d). Could not read from encoder ' \
                  'source (%s)\nException:\n%s' % \
                  (axis, self.attributes[axis]['encoder_source'],
                   str(e))

            self._log.error(msg)
            raise e

    def getEcamDatTable(self, axis):
        return self.ipap[axis].get_ecam_table()

    def setEcamDatTable(self, axis, value):
        self.ipap[axis].set_ecam_table(value)

    param2attr = {'indexer': 'indexer',
                  'poweron': 'power',
                  'infoa': 'infoa',
                  'infob': 'infob',
                  'infoc': 'infoc',
                  'enableencoder_5v': 'auxps',
                  'closedloop': 'pcloop',
                  'measurei': 'meas_i',
                  'posaxis': 'pos',
                  'posshftenc': 'pos_shftenc',
                  'postgtenc': 'pos_tgtenc',
                  'posencin': 'pos_encin',
                  'posinpos': 'pos_inpos',
                  'posabsenc': 'pos_absenc',
                  'posmotor': 'pos_motor',
                  'encaxis': 'enc',
                  'encshftenc': 'enc_shftenc',
                  'enctgtenc': 'enc_tgtenc',
                  'encencin': 'enc_encin',
                  'encinpos': 'enc_inpos',
                  'encabsenc': 'enc_absenc',
                  'ecamout': 'ecam',
                  'syncaux': 'syncaux',
                  'syncpos': 'syncpos',
                  'status5vpower': 'state_5vpower',
                  'statusdriverboard': 'status',
                  'statusalive': 'state_alive',
                  'statuscode': 'status',
                  'statuspoweron': 'state_poweron',
                  'statusdisable': 'state_disabled',
                  'statushome': 'state_inhome',
                  'statusindexer': 'state_indexer_str',
                  'statusinfo': 'state_info_code',
                  'statuslimpos': 'state_limit_positive',
                  'statuslimneg': 'state_limit_negative',
                  'statusmode': 'state_mode_str',
                  'statusmoving': 'state_moving',
                  'statusoutofwin': 'state_outofwin',
                  'statuspresent': 'state_present',
                  'statusready': 'state_ready',
                  'statussettling': 'state_settling',
                  'statusstopcode': 'state_stop_str',
                  'statusstopcodevalue': 'state_stop_code',
                  'statusverserr': 'state_verserr',
                  'statuswarning': 'state_warning',
                  'statusdetails': 'vstatus',
                  }

    def GetAxisExtraPar(self, axis, parameter):
        """ Get Icepap driver particular parameters.
        @param axis to get the parameter
        @param name of the parameter to retrive
        @return the value of the parameter
        """
        # the next 3 attribs dont reach the lower part of the function in
        # normal behaviour. mmm
        parameter = parameter.lower()
        if parameter == 'difaxmotor':
            return self.ipap[axis].pos - self.ipap[axis].pos_motor
        elif parameter == 'difaxtgtenc':
            return self.ipap[axis].pos - self.ipap[axis].pos_tgtenc
        elif parameter == 'difaxshftenc':
            return self.ipap[axis].pos - self.ipap[axis].pos_shftenc
        elif parameter == 'velmotor':
            return self.ipap[axis].get_velocity(vtype='MOTOR')
        elif parameter == 'velcurrent':
            return self.ipap[axis].get_velocity(vtype='CURRENT')
        elif parameter == 'syncres':
            # TODO implement attribute on axis class
            result = self.ipap[axis].send_cmd('?syncres')
            return ' '.join(result)
        elif parameter == 'statuslim-':
            parameter = 'statuslimneg'
            self._log.warning('Deprecation warning! ipython 5.5.0 is not '
                              'compatible.')
        elif parameter == 'statuslim+':
            parameter = 'statuslimpos'
            self._log.warning('Deprecation warning! ipython 5.5.0 is not '
                              'compatible.')

        attr = self.param2attr[parameter]
        result = self.ipap[axis].__getattribute__(attr)
        if parameter.startswith('info') or parameter in ('syncpos', 'syncaux'):
            result = ' '.join(result)
        return result

    def SetAxisExtraPar(self, axis, parameter, value):
        parameter = parameter.lower()
        if parameter == 'syncres':
            # TODO implement attribute on axis
            self.ipap[axis].send_cmd('syncres {}'.format(value))
            return
        if parameter.startswith('info') or parameter in ('syncpos', 'syncaux'):
            value = value.split()

        attr = self.param2attr[parameter]
        try:
            self.ipap[axis].__setattr__(attr, value)
        except Exception as e:
            self._log.error("%s %s", parameter, str(e))


    def SendToCtrl(self, cmd):
        """ Send the icepap native commands.
        @param cmd: command to send to the Icepap controller
        @return the result received
        """
        try:
            cmd = cmd.upper()
            res = self.ipap.send_cmd(cmd)
            if res is not None:
                return ' '.join(res)
            # added by zreszela on 8.02.2013
            else:
                return ""
        except Exception as e:
            # To provent huge logs, do not log this error until log levels
            # can be changed in per-controller basis
            # self._log.error('SendToCtrl(%s). No connection to %s.' % (cmd,
            #  self.Host))
            return 'Error: {0}'.format(e)

    def SetCtrlPar(self, parameter, value):
        param = parameter.lower()
        if param == 'pmux':
            # Multiple comma separated commands are allowed
            commands = value.lower().split(",")
            for command in commands:
                if 'remove' in command:
                    args = command.split()
                    dest = ''
                    if len(args) > 1:
                        dest = args[-1]
                    self.ipap.clear_pmux(dest=dest)
                else:
                    args = command.split()
                    if 'pmux' in args:
                        args.pop(args.index('pmux'))
                    if len(args) == 1:
                        self.ipap.add_pmux(source=args[0])
                    else:
                        hard = 'hard' in args
                        if hard:
                            args.pop(args.index('hard'))
                        pos = 'pos' in args
                        if pos:
                            args.pop(args.index('pos'))
                        aux = 'aux' in command
                        if aux:
                            args.pop(args.index('aux'))

                        source = args[0]
                        dest = ''
                        if len(args) == 2:
                            dest = args[1]
                        if not any([pos, aux]):
                            self.ipap.add_pmux(source=source, dest=dest)
                        else:
                            self.ipap.add_pmux(source=source, dest=dest,
                                               pos=pos, aux=aux, hard=hard)
        else:
            super(IcepapController, self).SetCtrlPar(parameter, value)

    def GetCtrlPar(self, parameter):
        param = parameter.lower()
        if param == 'pmux':
            value = '{0}'.format(self.ipap.get_pmux())
        else:
            value = super(IcepapController, self).GetCtrlPar(parameter)
        return value


##############################################################################
# THIS TWO CLASSES ARE NEEDED BECAUSE IT IS NOT POSSIBLE
# TO ACCESS THE DEVICE FROM A DEVICE CALL
##############################################################################
class FakedAttribute(object):
    def __init__(self, value):
        self.value = value


class FakedAttributeProxy(object):
    def __init__(self, controller, axis, attribute):
        self.ctrl = controller
        self.axis = axis
        self.attribute = attribute.replace('attr://', '')

    def read(self):
        value = self.ctrl.GetAxisExtraPar(self.axis, self.attribute)
        return FakedAttribute(value)
