import m5
from m5.objects import *

system = System()

#clock setup
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# setting up RAM memory mode to timing mode. This should probably mean,
# the load store operation delays are fixed to a time setting insteas of
# realtime dynamic time variation scenarios.
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create CPU based on timing as well.
# The default setting is all the instructions gets finished in 1 cycle.
system.cpu = TimingSimpleCPU()

# setup memory bus..
# is address bus + data bus together called as memory bus ?
# then address + data + control bus is overall system bus ?
system.membus = SystemXBar()

# setup cache config. here we are disabling cache by bypassing
# and directly conneting CPU to memory
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# create IO/Interrupt controller to handle mostly the
# interupts and mem IO control ports ?!?
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# not sure exactly what this mean....
# connecting all system port to the memory bus resquestor ? reqesting what ?
system.system_port = system.membus.cpu_side_ports

# create a memory controller with DRAM and
system.mem_ctrl = MemCtrl()
# creating a DDR3 RAM with 1600MHz 8x8 setting
# 8x8 mean 8gb x 8gb, total 64 gb ?
system.mem_ctrl.dram = DDR3_1600_8x8()
# set memory range as the system mem range set earlier
system.mem_ctrl.dram.range = system.mem_ranges[0]
# connecting mem_ctrl requestor port to membus responder port ? or otherise ?
system.mem_ctrl.port = system.membus.mem_side_ports

# now choose the program to be run on the designed CPU
binary = 'tests/test-progs/hello/bin/x86/linux/hello'

system.workload = SEWorkload.init_compatible(binary)

# create a process object and provide the command to be
# executed with the binary into the process.cmd
process = Process()
process.cmd = [binary]

# assign the process as the workload to the cpu
system.cpu.workload = process

# run the process..
system.cpu.createThreads()

# set the created system as the root of the m5 simulator to simulate.
root = Root(full_system = False, system = system)
m5.instantiate()

print("beginning simulation!")
exit_event = m5.simulate()

print('exiting @ tick {} beacause {}'
        .format(m5.curTick(), exit_event.getCause()))
