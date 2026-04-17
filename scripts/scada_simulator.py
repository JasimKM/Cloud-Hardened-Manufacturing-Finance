from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import logging

# Configure Logging for Manufacturing OT Monitoring
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

def run_scada_simulator():
    # Level 2 (SCADA/HMI) Data block simulation
    # Holding registers representing machine state:
    # 0: Spindle Speed (RPM)
    # 1: Temperature (Celsius)
    # 2: Unit Count
    # 3: Security Lock Status (1=Hardened, 0=Vulnerable)
    
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [2500, 42, 100, 1]),
        ir=ModbusSequentialDataBlock(0, [0]*100)
    )
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'ManufacturingVault-Industrial'
    identity.ProductCode = 'MV-SCADA-01'
    identity.VendorUrl = 'http://manufacturing-vault.internal'
    identity.ProductName = 'Purdue Model Level 2 Simulator'
    identity.ModelName = 'Cyber-Hardened-PLC'
    identity.MajorMinorRevision = '2.0.4'

    print("--- ManufacturingVault SCADA Simulator (Level 2) ---")
    print("Binding to: 0.0.0.0:502 (Default Modbus Port)")
    print("Access only permitted from MES (Level 3) subnet.")
    
    StartTcpServer(context=context, identity=identity, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_scada_simulator()
