from __future__ import annotations

import logging
from collections import namedtuple
from typing import ClassVar

from machine.datapath import DataPath, Enum, Selector
from machine.isa import HaltError, Instruction, Opcode, Port, TypesOfAddressing

microcode_fields_name = [
    "latch_cr",
    "sel_ip",
    "latch_ip",
    "sel_ar",
    "latch_ar",
    "sel_oe",
    "signal_oe",
    "sel_dr",
    "latch_dr",
    "latch_left_op",
    "latch_right_op",
    "signal_calculate",
    "check_flags",
    "sel_acc",
    "latch_acc",
    "sel_wr",
    "signal_wr",
    "sel_sp",
    "latch_sp",
    "latch_out",
    "mux_port",
    "latch_in",
    "mux_mPC",
    "latch_mPC"
]
signals = [
    "latch_cr",
    "latch_ip",
    "latch_ar",
    "signal_oe",
    "sel_dr",
    "latch_dr",
    "latch_left_op",
    "latch_right_op",
    "signal_calculate",
    "latch_acc",
    "signal_wr",
    "latch_sp",
    "latch_in",
    "latch_out"
]
selectors = {
    "latch_ip": "sel_ip",
    "latch_ar": "sel_ar",
    "signal_oe": "sel_oe",
    "latch_dr": "sel_dr",
    "latch_acc": "sel_acc",
    "signal_wr": "sel_wr",
    "latch_sp": "sel_sp",
    "latch_in": "mux_port",
    "latch_out": "mux_port",
    "latch_mPC": "mux_mPC",
}


class MicrocodeSelector(Enum):
    INCREMENT = "INCREMENT"
    DECODE = "DECODE"
    RESET = "RESET"


Microcode = namedtuple("Microcode", microcode_fields_name)


class Decoder:
    microcode: ClassVar[list] = []

    def decode_instruction(self, instruction: Instruction) -> list[Microcode]:
        self.microcode = []
        types_of_addressing = instruction.arg1
        self.operand_fetch(types_of_addressing)
        self.execute_command_fetch(instruction)
        return self.microcode

    def execute_command_fetch(self, instruction: Instruction):
        opcode = instruction.opcode
        instr = []
        if opcode == Opcode.HALT:
            raise HaltError
        math_commands = [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.INC]
        jump_commands = [Opcode.JA, Opcode.JB, Opcode.JNE, Opcode.JE]
        options = []
        if opcode in math_commands:
            options.append(
                {"latch_left_op": 1,
                 "latch_right_op": 1,
                 "signal_calculate": 1,
                 "sel_acc": Selector.FROM_ALU,
                 "latch_acc": 1})
        elif opcode in jump_commands:
            options.append({"check_flags": 1})
            options.append({"sel_ip": Selector.FROM_DR, "latch_ip": 1})
        else:
            commands = {
                Opcode.JUMP: [{"sel_ip": Selector.FROM_DR, "latch_ip": 1}],
                Opcode.LD: [{"sel_acc": Selector.FROM_DR, "latch_acc": 1}],
                Opcode.ST: [{"sel_wr": Selector.FROM_AR, "signal_wr": 1}],
                Opcode.PUSH: [{"sel_wr": Selector.FROM_SP, "signal_wr": 1, "sel_sp": Selector.SEL_DEC, "latch_sp": 1}],
                Opcode.POP: [{"sel_sp": Selector.SEL_INC, "latch_sp": 1},
                             {"sel_dr": Selector.FROM_SP, "latch_dr": 1},
                             {"sel_acc": Selector.FROM_DR, "latch_acc": 1}],
                Opcode.CMP: [{"latch_left_op": 1, "latch_right_op": 1, "signal_calculate": 1}],
                Opcode.READ: [{"mux_port": Port.BUFFER_IN, "latch_in": 1},
                              {"sel_acc": Selector.FROM_INPUT, "latch_acc": 1}],
                Opcode.PRINT: [{"mux_port": Port.OUT, "latch_out": 1}]

            }
            options = commands[opcode]

        for option in options:
            instr.append(self.create_micro_instr(option, MicrocodeSelector.INCREMENT))
        instr.append(self.create_micro_instr({}, MicrocodeSelector.RESET))
        self.microcode += instr

    def operand_fetch(self, types_of_addressing: str):
        if types_of_addressing == TypesOfAddressing.DIRECT.value:
            self.microcode.append(self.create_micro_instr({"sel_dr": Selector.FROM_CR, "latch_dr": 1}))
        if types_of_addressing == TypesOfAddressing.ABSOLUT.value or types_of_addressing == TypesOfAddressing.RELATIVE.value:
            self.microcode.append(self.create_micro_instr({"sel_ar": Selector.FROM_CR, "latch_ar": 1}))
        if types_of_addressing == TypesOfAddressing.RELATIVE.value:
            self.microcode.append(self.create_micro_instr({"sel_ar": Selector.FROM_MEMORY, "latch_ar": 1}))
        if types_of_addressing == TypesOfAddressing.ABSOLUT.value or types_of_addressing == TypesOfAddressing.RELATIVE.value:
            self.microcode.append(self.create_micro_instr({"sel_dr": Selector.FROM_MEMORY, "latch_dr": 1}))

    def instruction_fetch(self) -> list[Microcode]:
        return [
            self.create_micro_instr({"latch_cr": 1, "sel_ip": Selector.FROM_IP, "latch_ip": 1},
                                    MicrocodeSelector.DECODE)]

    def create_micro_instr(self, options: dict, mux_mpc: MicrocodeSelector = MicrocodeSelector.INCREMENT) -> Microcode:
        options["mux_mPC"] = mux_mpc
        options["latch_mPC"] = 1
        tmp = [0] * (len(microcode_fields_name))
        for key in options.keys():
            tmp[microcode_fields_name.index(key)] = options.get(key)
        return Microcode._make(tmp)


class ControlUnit:
    def __init__(self, data_path: DataPath, tick_limit: int):
        self.data_path = data_path
        self.tick_counter = 0
        self.tick_limit = tick_limit
        self.decoder = Decoder()
        self.microcode_memory: list[Microcode] = []
        self.microcode_memory = self.decoder.instruction_fetch().copy()
        self.microcode_ip = 0

    def process_tick(self):
        self.tick_counter += 1
        current_microcode = self.microcode_memory[self.microcode_ip]
        for signal_name in current_microcode._fields:
            if getattr(current_microcode, signal_name) != 1:
                continue
            if signal_name in signals:
                self.send_signal_to_data_path(signal_name)
            if signal_name == "latch_mPC":
                self.microcode_handler(signal_name)
            if signal_name == "check_flags":
                self.check_flags()

    def send_signal_to_data_path(self, signal_name: str):
        assert signal_name in signals, "incorrect signal to DataPath"
        if selectors.get(signal_name):
            sel = self.get_selector(signal_name)
            getattr(self.data_path, signal_name)(sel)
        else:
            getattr(self.data_path, signal_name)()

    def microcode_handler(self, signal_name: str):
        sel = self.get_selector(signal_name)
        if sel == MicrocodeSelector.INCREMENT:
            self.microcode_ip += 1
        if sel == MicrocodeSelector.DECODE:
            self.microcode_memory += self.decoder.decode_instruction(self.data_path.cr)
            self.microcode_ip += 1
        if sel == MicrocodeSelector.RESET:
            logging.info(self.__repr__())
            self.microcode_ip = 0
            self.microcode_memory = self.decoder.instruction_fetch().copy()

    def check_flags(self):
        zero_flag, negative_flag = self.data_path.get_flags()
        if not (
                self.data_path.cr.opcode == Opcode.JE
                and zero_flag == 1
                or self.data_path.cr.opcode == Opcode.JA
                and (negative_flag == 0)
                or self.data_path.cr.opcode == Opcode.JB
                and (negative_flag == 1 or zero_flag == 1)
                or self.data_path.cr.opcode == Opcode.JNE
                and zero_flag == 0
        ):
            self.microcode_ip += 1

    def get_selector(self, signal_name: str) -> Selector:
        return getattr(self.microcode_memory[self.microcode_ip], selectors.get(signal_name))

    def __repr__(self):

        return "execute_command {:>15} | tick: {:10d} | ip: {:10d} | dr {:10d} |ar: {:10d} | acc: {:10d} | sp: {:10d}".format(
            self.data_path.cr.opcode,
            self.tick_counter,
            self.data_path.ip,
            self.data_path.dr,
            self.data_path.ar,
            self.data_path.acc,
            self.data_path.sp
        )
