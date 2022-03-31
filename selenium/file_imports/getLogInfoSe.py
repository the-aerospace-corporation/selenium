from .AMUDataContainer import AMUDataContainer

class getLogInfoSe(AMUDataContainer):
    def __init__(self, log_file):
        AMUDataContainer.__init__(self)
        self.AMUs = []
        self.cell_holders = 0
        attributes = list(self.__dict__.keys())
        attributes.remove('AMUs')
        attributes.remove('cell_holders')
        with open(log_file,'rU') as f:
            for j in f:
                line = j.rstrip('\n')
                if line:
                    m = line.split('\t')
                    if ('address' in line) or ('address:' in line):
                        amu = AMUDataContainer()
                        amu.address = int(line.split(': ')[-1], 16)
                    # if len(m) == 1:
                    #     n = m[0].split()
                        # address = int(m[0].split(':')[1], 16)
                    # elif len(m) == 2:
                    #     n = m[1].split()
                        # address = int(m[1].split(':')[-1], 16)
                        # if ('address' in n) or ('address:' in n):


                    elif len(m) > 1:
                        n = m[1].split(' ')
                        if ':DUT:MANUFACTURER:' in n:
                            amu.manufacturer = n[1]

                        elif ':DUT:MODEL:' in n:
                            amu.model = n[1]

                        elif ':DUT:TECH:' in n:
                            amu.tech = n[1]

                        elif ':DUT:SERIAL:' in n:
                            amu.cell_id = m[1].split(': ')[-1]

                        elif ':DUT:JUNCTION:' in n:
                            amu.junction = (float(n[1]))

                        elif ':DUT:COVERGLASS:' in n:
                            amu.coverglass = (float(n[1]))

                        elif ':DUT:ENERGY:' in n:
                            amu.energy = (float(n[1]))

                        elif ':DUT:DOSE:' in n:
                            amu.fluence = (float(n[1]))

                        elif ':DUT:NOTES:' in n:
                            amu.notes = m[1].split(':')[3]

                        elif ':FIRMWARE:' in n:
                            amu.firmware_version = n[1]

                        elif ':SERIAL:' in n:
                            amu.serial = n[1]

                        elif ':AMU' in n:
                            n = m[1].split()
                            amu.amu_number = (int(float(n[1])))
                            self.AMUs.append(amu)
                            self.cell_holders += 1

                        elif 'READY*****' in n:
                            break

        for attr in attributes:
            attr_data = []
            for amu in self.AMUs:
                if hasattr(amu, attr):
                    attr_data.append(getattr(amu, attr))

            setattr(self, attr, attr_data)




