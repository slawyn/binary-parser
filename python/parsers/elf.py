import struct
import sys
import os
from utils import *

original_absfile = []
edited_absfile = []
segment_starting_offsets = []
segment_starting_addresses = []
segment_ending_offsets = []
segment_ending_addresses = []

original_segment_offset =0


COPY_FLASH = 0x10000
ORIGINAL_LOWEST_ADDRESS = 0x8000000
ORIGINAL_HIGHEST_ADDRESS = ORIGINAL_LOWEST_ADDRESS+COPY_FLASH#0x800FFFF

COPY_LOWEST_ADDRESS = ORIGINAL_HIGHEST_ADDRESS
COPY_HIGHEST_ADDRESS = ORIGINAL_HIGHEST_ADDRESS+COPY_FLASH#0x801FFFF

OFFSET = 0






class ElfHeader:
	"""Elf Header
	"""
	EI_MAG = 0x00
	EI_MAG_SZ = 4

	EI_CLASS = EI_MAG + EI_MAG_SZ
	EI_CLASS_SZ = 1
	EI_CLASS_T = {1:"ELF32", 2:"ELF64"}

	EI_DATA = EI_CLASS + EI_CLASS_SZ
	EI_DATA_SZ = 1
	EI_DATA_T = {1:"Little Endian", 2:"Big Endian"}

	EI_VERSION = EI_DATA + EI_DATA_SZ
	EI_VERSION_SZ = 1
	EI_VERSION_T = {0:"0 (Old)", 1:"1 (Current)"}

	EI_OSABI = EI_VERSION + EI_VERSION_SZ
	EI_OSABI_SZ = 1
	EI_OSABI_T = {0x00:"System V", 0x01:"HP-UX", 0x02:"NetBSD", 0x03:"Linux", 0x04:"GNU Hurd", 0x06:"Solaris", 0x07:"AIX", 0x08:"IRIX", 0x09:"FreeBSD", 0x0A:"Tru64", 0x0B:"Novell Modesto", 0x0C:"OpenBSD", 0x0D:"OpenVMS", 0x0E:"NonStop Kernel", 0x0F:"AROS", 0x10:"FenixOS", 0x011:"Nuxi CloudABI", 0x12:"Stratus Technologies OpenVOS"}

	EI_ABIVERSION = EI_OSABI + EI_OSABI_SZ
	EI_ABIVERSION_SZ = 1
	EI_ABIVERSION_T = {0:"0 (Standard)"}

	EI_PAD = EI_ABIVERSION + EI_ABIVERSION_SZ
	EI_PAD_SZ = 7

	EI_SZ = EI_MAG_SZ + EI_CLASS_SZ + EI_DATA_SZ + EI_VERSION_SZ + EI_OSABI_SZ + EI_ABIVERSION_SZ + EI_PAD_SZ

	E_TYPE = EI_SZ
	E_TYPE_SZ = 2
	E_TYPE_T = { 0x00:"ET_NONE (Unknown)", 0x01:"ET_REL (Relocatable file)", 0x02:"ET_EXEC (Executable file)", 0x03:"ET_DYN (Shared object)", 0x04:"ET_CORE (Core file)", 0xFE00:"ET_LOOS (OS Specific)", 0xFEFF:"ET_HIOS (OS Specific)", 0xFF00:"ET_LOPROC (CPU specific)", 0xFFFF:"ET_HIPROC (CPU specific)"}

	E_MACHINE = E_TYPE + E_TYPE_SZ
	E_MACHINE_SZ = 2
	E_MACHINE_T = {	0x00:"Not Specified", 0x01:"AT&T WE 32100", 0x02:"SPARC", 0x03:"x86", 0x04:"Motorola 68000 (M68k)", 0x05:"Motorola 68000 (M88k)",\
	 				0x06:"Intel MCU", 0x07:"Intel 80860", 0x08:"MIPS", 0x09:"IBM System370", 0x0A:"MIPS RS3000 Little-endian", 0x0B:"Future use", 0x0C:"Future use",\
				 	0x0D:"Future use", 0x0E:"Hewlett-Packard PA-RISC", 0x0F:"Future use", 0x13:"Intel 80960", 0x14:"PowerPC", 0x15:"PowerPC(64-bit)", 0x16:"S390, S390x",\
				 	0x17:"IBM SPU/SPC", 0x18:"Future use", 0x19:"Future use", 0x1A:"Future use", 0x1B:"Future use", 0x1C:"Future use", 0x1D:"Future use", 0x1E:"Future use",\
					0x1F:"Future use", 0x20:"Future use", 0x21:"Future use", 0x22:"Future use", 0x23:"Future use", 0x24:"NEC V800", 0x25:"Fujitsu FR20", 0x26:"TRW RH-32",\
					0x27:"Motorola RCE", 0x28:"ARM (up to ARMv7/Aarch32)", 0x29:"Digital Alpha", 0x2A:"SuperH", 0x2B:"SPARC Version 9", 0x2C:"Siemens TriCore", 0x2D:"Argonaut RISC Core",\
					0x2E:"Hitachi H8/300", 0x2F:"Hitachi H8/300H", 0x30:"Hitachi H8S", 0x31:"Hitachi H8/500", 0x32:"IA-64", 0x33:"Stanford MIPS-X", 0x34:"Motorola ColdFire",\
					0x35:"Motorola M68HC12", 0x36:"Fujitsu MMA Multimedia Accelerator", 0x37:"Siemens PCP", 0x38:"Sony nCPU embedded RISC processor", 0x39:"Denso NDR1 microprocessor",\
					0x3A:"Motorola Star*Core processor", 0x3B:"Toyota ME16 processor", 0x3C:"STMicroelectronics ST100 processor", 0x3D:"Advanced Logic Corp. TinyJ embedded processor family",\
					0x3E:"AMD x86-64", 0x8C:"TMS320C6000 Family", 0xAF:"MCST Elbrus e2k", 0xB7:"ARM 64-bits (ARMv8/Aarch64)", 0xF3:"RISC-V", 0xF7:"Berkeley Packet Filter", 0x101:"WDC 65C816"}

	E_VERSION = E_MACHINE + E_MACHINE_SZ
	E_VERSION_SZ = 4
	E_VERSION_T = {0x01: "1 (Original)"}

	# Version
	E_ENTRY = E_VERSION + E_VERSION_SZ
	E_ENTRY_SZ = 4
	E_ENTRY64 = E_VERSION + E_VERSION_SZ
	E_ENTRY64_SZ = 8

	# Programm Headers
	E_PHOFF = E_ENTRY + E_ENTRY_SZ
	E_PHOFF_SZ = 4
	E_PHOFF64 = E_ENTRY64 + E_ENTRY64_SZ
	E_PHOFF64_SZ = 8

	# Sections
	E_SHOFF = E_PHOFF + E_PHOFF_SZ
	E_SHOFF_SZ = 4
	E_SHOFF64 = E_PHOFF64 + E_PHOFF64_SZ
	E_SHOFF64_SZ = 8

	# Flags
	E_FLAGS = E_SHOFF + E_SHOFF_SZ
	E_FLAGS_SZ = 4
	E_FLAGS64 = E_SHOFF64 + E_SHOFF64_SZ
	E_FLAGS64_SZ = E_FLAGS_SZ

	# This headers size
	E_EHSIZE = E_FLAGS + E_FLAGS_SZ
	E_EHSIZE_SZ = 2
	E_EHSIZE64 = E_FLAGS64 + E_FLAGS64_SZ
	E_EHSIZE64_SZ = E_EHSIZE_SZ

	# Program header entry size
	E_PHENTSIZE = E_EHSIZE + E_EHSIZE_SZ
	E_PHENTSIZE_SZ = 2
	E_PHENTSIZE64 = E_EHSIZE64 + E_EHSIZE64_SZ
	E_PHENTSIZE64_SZ = E_PHENTSIZE_SZ

	# Program headers' count
	E_PHNUM = E_PHENTSIZE + E_PHENTSIZE_SZ
	E_PHNUM_SZ = 2
	E_PHNUM64 = E_PHENTSIZE64 + E_PHENTSIZE64_SZ
	E_PHNUM64_SZ = E_PHNUM_SZ

	# Section header entry size
	E_SHENTSIZE = E_PHNUM + E_PHNUM_SZ
	E_SHENTSIZE_SZ = 2
	E_SHENTSIZE64 = E_PHNUM64 + E_PHNUM64_SZ
	E_SHENTSIZE64_SZ = E_SHENTSIZE_SZ

	# Section headers' count
	E_SHNUM = E_SHENTSIZE + E_SHENTSIZE_SZ
	E_SHNUM_SZ = 2
	E_SHNUM64 = E_SHENTSIZE64 + E_SHENTSIZE64_SZ
	E_SHNUM64_SZ = E_SHNUM_SZ

	E_SHSTRNDX = E_SHNUM + E_SHNUM_SZ
	E_SHSTRNDX_SZ = 2
	E_SHSTRNDX64 = E_SHNUM64 + E_SHNUM64_SZ
	E_SHSTRNDX64_SZ = E_SHSTRNDX_SZ

	def __init__(self, buffer):
		"""Parse Header
		"""

		# Identification
		self.e_ident =   buffer[ElfHeader.EI_MAG:ElfHeader.EI_SZ]
		if self.e_ident[ElfHeader.EI_CLASS] == 2:
			self.opt_64bit = True
		else:
			self.opt_64bit = False

		if self.e_ident[ElfHeader.EI_DATA] == 2:
			self.opt_big_endian = True
		else:
			self.opt_big_endian = False

		self.e_type =    buffer[ElfHeader.E_TYPE:ElfHeader.E_TYPE + ElfHeader.E_TYPE_SZ]
		self.e_machine = buffer[ElfHeader.E_MACHINE:ElfHeader.E_MACHINE + ElfHeader.E_MACHINE_SZ]
		self.e_version = buffer[ElfHeader.E_VERSION:ElfHeader.E_VERSION + ElfHeader.E_VERSION_SZ]


		# load 64 bit system dependant offsets
		if self.opt_64bit:
			ElfHeader.E_ENTRY = ElfHeader.E_ENTRY64
			ElfHeader.E_ENTRY_SZ = ElfHeader.E_ENTRY64_SZ
			ElfHeader.E_PHOFF = ElfHeader.E_PHOFF64
			ElfHeader.E_PHOFF_SZ = ElfHeader.E_PHOFF64_SZ
			ElfHeader.E_SHOFF = ElfHeader.E_SHOFF64
			ElfHeader.E_SHOFF_SZ = ElfHeader.E_SHOFF64_SZ
			ElfHeader.E_FLAGS = ElfHeader.E_FLAGS64
			ElfHeader.E_FLAGS_SZ = ElfHeader.E_FLAGS64_SZ
			ElfHeader.E_EHSIZE = ElfHeader.E_EHSIZE64
			ElfHeader.E_EHSIZE_SZ = ElfHeader.E_EHSIZE64_SZ
			ElfHeader.E_PHENTSIZE = ElfHeader.E_PHENTSIZE64
			ElfHeader.E_PHENTSIZE_SZ = ElfHeader.E_PHENTSIZE64_SZ
			ElfHeader.E_PHNUM = ElfHeader.E_PHNUM64
			ElfHeader.E_PHNUM_SZ = ElfHeader.E_PHNUM64_SZ
			ElfHeader.E_SHENTSIZE = ElfHeader.E_SHENTSIZE64
			ElfHeader.E_SHENTSIZE_SZ = ElfHeader.E_SHENTSIZE64_SZ
			ElfHeader.E_SHNUM = ElfHeader.E_SHNUM64
			ElfHeader.E_SHNUM_SZ = ElfHeader.E_SHNUM64_SZ
			ElfHeader.E_SHSTRNDX = ElfHeader.E_SHSTRNDX64
			ElfHeader.E_SHSTRNDX_SZ = ElfHeader.E_SHSTRNDX64_SZ

		self.e_entry = 		buffer[ElfHeader.E_ENTRY:ElfHeader.E_ENTRY+ElfHeader.E_ENTRY_SZ]
		self.e_phoff = 		buffer[ElfHeader.E_PHOFF:ElfHeader.E_PHOFF+ElfHeader.E_PHOFF_SZ]
		self.e_shoff = 		buffer[ElfHeader.E_SHOFF:ElfHeader.E_SHOFF+ElfHeader.E_SHOFF_SZ]
		self.e_flags = 		buffer[ElfHeader.E_FLAGS:ElfHeader.E_FLAGS+ElfHeader.E_FLAGS_SZ]
		self.e_ehsize = 	buffer[ElfHeader.E_EHSIZE:ElfHeader.E_EHSIZE+ElfHeader.E_EHSIZE_SZ]
		self.e_phentsize = 	buffer[ElfHeader.E_PHENTSIZE:ElfHeader.E_PHENTSIZE+ElfHeader.E_PHENTSIZE_SZ]
		self.e_phnum = 		buffer[ElfHeader.E_PHNUM:ElfHeader.E_PHNUM+ElfHeader.E_PHNUM_SZ]
		self.e_shentsize = 	buffer[ElfHeader.E_SHENTSIZE:ElfHeader.E_SHENTSIZE+ElfHeader.E_SHENTSIZE_SZ]
		self.e_shnum = 		buffer[ElfHeader.E_SHNUM:ElfHeader.E_SHNUM+ElfHeader.E_SHNUM_SZ]
		self.e_shstrndx = 	buffer[ElfHeader.E_SHSTRNDX:ElfHeader.E_SHSTRNDX+ElfHeader.E_SHSTRNDX_SZ]


	def get_type(self):
		"""Get Type
		"""
		code = unpack(self.e_type, self.opt_big_endian)
		if code in ElfHeader.E_TYPE_T:
			return ElfHeader.E_TYPE_T[code]
		return "Unknown"

	def get_machine(self):
		"""Get Machine
		"""
		code = unpack(self.e_machine, self.opt_big_endian)
		if code in ElfHeader.E_MACHINE_T:
			return ElfHeader.E_MACHINE_T[code]
		return "Unknown"

	def get_version(self):
		"""Get Version
		"""
		code = unpack(self.e_version, self.opt_big_endian)
		if code in ElfHeader.E_VERSION_T:
			return ElfHeader.E_VERSION_T[code]
		return "Unknown"

	def get_entry(self):
		"""Get Entry
		"""
		return unpack(self.e_entry, self.opt_big_endian)

	def get_ph_offset(self):
		"""Get Program Headers Offset
		"""
		return unpack(self.e_phoff, self.opt_big_endian)

	def get_sh_offset(self):
		"""Get Section Headers Offset
		"""
		return unpack(self.e_shoff, self.opt_big_endian)

	def get_header_size(self):
		"""Get Header Size
		"""
		return unpack(self.e_ehsize, self.opt_big_endian)

	def get_phent_size(self):
		"""Get Program Entry Size
		"""
		return unpack(self.e_phentsize, self.opt_big_endian)

	def get_phnum_num(self):
		"""Get Program Entry Count
		"""
		return unpack(self.e_phnum, self.opt_big_endian)

	def get_shent_size(self):
		"""Get Section Entry Size
		"""
		return unpack(self.e_shentsize, self.opt_big_endian)

	def get_shnum_num(self):
		"""Get Section Entry Count
		"""
		return unpack(self.e_shnum, self.opt_big_endian)

	def get_shstr_ndx(self):
		"""Get String Section Index
		"""
		return unpack(self.e_shstrndx, self.opt_big_endian)

	def get_opt_bigendian(self):
		"""Get Big Endian
		"""
		return self.opt_big_endian

	def get_opt_64bit(self):
		"""Get 64 bit
		"""
		return self.opt_64bit

	def print_all(self):
		"""Print all
		"""
		log("ELF Header:")
		log("\t%-1s%-20s"%("Magic:", self.e_ident))
		log("\t%-50s%-20s"%("Class:", ElfHeader.EI_CLASS_T[self.e_ident[ElfHeader.EI_CLASS]]))
		log("\t%-50s%-20s"%("Data:", ElfHeader.EI_DATA_T[self.e_ident[ElfHeader.EI_DATA]]))
		log("\t%-50s%-20s"%("Version:", ElfHeader.EI_VERSION_T[self.e_ident[ElfHeader.EI_VERSION]]))
		log("\t%-50s%-20s"%("OS/ABI:", ElfHeader.EI_OSABI_T[self.e_ident[ElfHeader.EI_OSABI]]))
		log("\t%-50s%-20s"%("ABI Version:", ElfHeader.EI_ABIVERSION_T[self.e_ident[ElfHeader.EI_ABIVERSION]]))
		log("\t%-50s%-20s"%("Type:", self.get_type()))
		log("\t%-50s%-20s"%("Machine:", self.get_machine()))
		log("\t%-50s%-20s"%("Version:", self.get_version()))
		log("\t%-50s0x%-20x"%("Entry point address:", self.get_entry()))
		log("\t%-50s0x%-20x"%("Program headers file offset:", self.get_ph_offset()))
		log("\t%-50s0x%-20x"%("Section headers file offset:", self.get_sh_offset()))
		log("\t%-50s0x%-20x"%("Flags:", unpack(self.e_flags, self.opt_big_endian)))
		log("\t%-50s%-20s(bytes)"%("Size of this header:",self.get_header_size()))
		log("\t%-50s%-20s(bytes)"%("Size of program headers:",self.get_phent_size()))
		log("\t%-50s%-20s"%("Number of program headers:", self.get_phnum_num()))
		log("\t%-50s%-20s(bytes)"%("Size of section headers:", self.get_shent_size()))
		log("\t%-50s%-20s"%("Number of section headers:", self.get_shnum_num()))
		log("\t%-50s%-20s"%("Section header string table index:", self.get_shstr_ndx()))

class ProgramHeader:
	"""Program Header
	"""
	# 32 bit
	P_TYPE = 0x00
	P_TYPE_SZ = 4
	P_TYPE_T = {0x00000000:"PT_NULL (Unused)", 0x00000001:"PT_LOAD (Loadable segment)",0x00000002:"PT_DYNAMIC (Dynamic linking information)",\
				0x00000003:"PT_INTERP (Interpreter information)",0x00000004:"PT_NOTE (Auxiliary information)",0x00000005:"PT_SHLIB (Reserved)",\
				0x00000006:"PT_PHDR (Contains program header table)",0x00000007:"PT_TLS (Thread-Local Storage template)",0x60000000:"PT_LOOS (OS specific)",\
				0x6474e550:"PT_GNU_EH_FRAME (Unwind information)", 0x6474e551:"PT_GNU_STACK (Stack flags)", 0x6474e552:"PT_GNU_RELRO (Read-only after relocation)",\
				0x6474e553:"PT_GNU_PROPERTY (Comment)", 0x6FFFFFFF:"PT_HIOS (OS specific)", 0x70000000:"PT_LOPROC (CPU specific)", 0x7FFFFFFF:"PT_HIPROC (CPU specific)"}

	P_OFFSET = 0x04
	P_OFFSET_SZ = 4

	P_VADDR = 0x08
	P_VADDR_SZ = 4

	P_PADDR = 0x0C
	P_PADDR_SZ = 4

	P_FILESZ = 0x10
	P_FILESZ_SZ = 4

	P_MEMSZ = 0x14
	P_MEMSZ_SZ = 4

	P_FLAGS = 0x18
	P_FLAGS_SZ = 4
	#{0x01:"PF_X (Execute)", 0x02:"PF_W (Write)", 0x04:"PF_R (Read)", 0xf0000000:"PF_MASKPROC (Unspecified)", }
	P_FLAGS_T = {0x01:"X", 0x02:"W", 0x04:"R", 0xf0000000:"U", }

	P_ALIGN = 0x1C
	P_ALIGN_SZ = 4

	# 64 bit
	P_TYPE64 = 0x00
	P_TYPE64_SZ = 4

	P_FLAGS64 = 0x04
	P_FLAGS64_SZ = 4

	P_OFFSET64 = 0x08
	P_OFFSET64_SZ = 8

	P_VADDR64 = 0x10
	P_VADDR64_SZ = 8

	P_PADDR64 = 0x18
	P_PADDR64_SZ = 8

	P_FILESZ64 = 0x20
	P_FILESZ64_SZ = 8

	P_MEMSZ64 = 0x28
	P_MEMSZ64_SZ = 8

	P_ALIGN64 = 0x30
	P_ALIGN64_SZ = 8

	def __init__(self, buffer, ph_idx, phent_off, phent_sz, opt_64bit, opt_big_endian):
		self.opt_64bit = opt_64bit
		self.opt_big_endian = opt_big_endian
		self.opt_idx = ph_idx
		phent_off += (ph_idx*phent_sz)
		if self.opt_64bit:
			self.p_type = buffer[phent_off + ProgramHeader.P_TYPE64: phent_off + ProgramHeader.P_TYPE64 + ProgramHeader.P_TYPE64_SZ]
			self.p_flags = buffer[phent_off + ProgramHeader.P_FLAGS64: phent_off + ProgramHeader.P_FLAGS64 + ProgramHeader.P_FLAGS64_SZ]
			self.p_offset = buffer[phent_off + ProgramHeader.P_OFFSET64: phent_off + ProgramHeader.P_OFFSET64 + ProgramHeader.P_OFFSET64_SZ]
			self.p_vaddr = buffer[phent_off + ProgramHeader.P_VADDR64: phent_off + ProgramHeader.P_VADDR64 + ProgramHeader.P_VADDR64_SZ]
			self.p_paddr = buffer[phent_off + ProgramHeader.P_PADDR64: phent_off + ProgramHeader.P_PADDR64 + ProgramHeader.P_PADDR64_SZ]
			self.p_filesz = buffer[phent_off + ProgramHeader.P_FILESZ64: phent_off + ProgramHeader.P_FILESZ64 + ProgramHeader.P_FILESZ64_SZ]
			self.p_memsz = buffer[phent_off + ProgramHeader.P_MEMSZ64: phent_off + ProgramHeader.P_MEMSZ64 + ProgramHeader.P_MEMSZ64_SZ]
			self.p_align = buffer[phent_off + ProgramHeader.P_ALIGN64: phent_off + ProgramHeader.P_ALIGN64 + ProgramHeader.P_ALIGN64_SZ]
		else:
			self.p_type = buffer[phent_off + ProgramHeader.P_TYPE: phent_off + ProgramHeader.P_TYPE + ProgramHeader.P_TYPE_SZ]
			self.p_flags = buffer[phent_off + ProgramHeader.P_FLAGS: phent_off + ProgramHeader.P_FLAGS + ProgramHeader.P_FLAGS_SZ]
			self.p_offset = buffer[phent_off + ProgramHeader.P_OFFSET: phent_off + ProgramHeader.P_OFFSET + ProgramHeader.P_OFFSET_SZ]
			self.p_vaddr = buffer[phent_off + ProgramHeader.P_VADDR: phent_off + ProgramHeader.P_VADDR + ProgramHeader.P_VADDR_SZ]
			self.p_paddr = buffer[phent_off + ProgramHeader.P_PADDR: phent_off + ProgramHeader.P_PADDR + ProgramHeader.P_PADDR_SZ]
			self.p_filesz = buffer[phent_off + ProgramHeader.P_FILESZ: phent_off + ProgramHeader.P_FILESZ + ProgramHeader.P_FILESZ_SZ]
			self.p_memsz = buffer[phent_off + ProgramHeader.P_MEMSZ: phent_off + ProgramHeader.P_MEMSZ + ProgramHeader.P_MEMSZ_SZ]
			self.p_align = buffer[phent_off + ProgramHeader.P_ALIGN: phent_off + ProgramHeader.P_ALIGN + ProgramHeader.P_ALIGN_SZ]


	def get_type(self):
		"""Get Type
		"""
		code = unpack(self.p_type, self.opt_big_endian)
		if code in ProgramHeader.P_TYPE_T:
			return ProgramHeader.P_TYPE_T[code]
		return "Unknown"

	def get_flags(self):
		"""Get Flags
		"""
		out = ""
		code = unpack(self.p_flags, self.opt_big_endian)
		for x in ProgramHeader.P_FLAGS_T:
			if (code & x)>0:
				out += ProgramHeader.P_FLAGS_T[x]
				code = code & (~x)
		# Unknown code
		if code>0:
			return out+"N"
		return out

	def print_all(self):
		"""Print all
		"""
		log("")
		log("\t[%-s]"%(self.opt_idx))
		log("\t%-50s%-20s"%("Type:", self.get_type()))
		log("\t%-50s0x%-20x"%("Offset:", unpack(self.p_offset, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Virtual Address:", unpack(self.p_vaddr, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Physical Address:", unpack(self.p_paddr, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Size in File:", unpack(self.p_filesz, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Size in Memory:", unpack(self.p_memsz, self.opt_big_endian)))
		log("\t%-50s%-20s"%("Flags:", self.get_flags()))
		log("\t%-50s0x%-20x"%("Align:",unpack(self.p_align, self.opt_big_endian)))

class SectionHeader:
	"""Section Header
	"""
	SH_NAME = 0x00
	SH_NAME_SZ = 4		# .shstrab offset

	SH_TYPE = 0x04
	SH_TYPE_SZ = 4
	SH_TYPE_T = {	0x00:"SHT_NULL (Unused)", 0x01:"SHT_PROGBITS (Program data)", 0x02:"SHT_SYMTAB (Symbol table)", 0x03:"SHT_STRTAB (String table)",\
					0x04:"SHT_RELA (Relocation entries with addends)", 0x05:"SHT_HASH (Symbol hash table)", 0x06:"SHT_DYNAMIC (Dynamic linking inmformation)",\
					0x07:"SHT_NOTE (Notes)", 0x08:"SHT_NOBITS (bss)", 0x09:"SHT_REL (Relocation entries, no addends)", 0x0A:"SHT_SHLIB (Reserved)",\
					0x0B:"SHT_DYNSYM (Dynamic linker symbol table)", 0x0E:"SHT_INIT_ARRAY (Array of constructors)", 0x0F:"SHT_FINI_ARRAY (Array of destructors)",\
					0x10:"SHT_PREINIT_ARRAY (Array of pre-constructors)", 0x11:"SHT_GROUP (Section group)", 0x12:"SHT_SYMTAB_SHDX (Extended section indices)",\
					0x13:"SHT_NUM (Number of defined types)", 0x60000000:"Start OS-specific"}

	SH_FLAGS = 0x08
	SH_FLAGS_SZ = 4
	SH_FLAGS_T  ={ 0x00:"",  0x01:"SHF_WRITE", 0x02:"SHF_ALLOC", 0x04:"SHF_EXECINSTR", 0x10:"SHF_MERGE",\
	  			   0x20:"SHF_STRINGS", 0x40:"SHF_INFO_LINK", 0x80:"SHF_LINK_ORDER", 0x100:"SHF_OS_NONCONFORMING",\
	  	   		   0x200:"SHF_GROUP", 0x400:"SHF_TLS", 0x0FF00000:"SHF_MASKOS", 0xF0000000:"SHF_MASKPROC",\
				   0x800:"SHF_COMPRESSED",\
				   0x4000000:"SHF_ORDERED", 0x8000000:"SHF_EXCLUDE"}
	'''
	{ 0x01:"SHF_WRITE (Writable)", 0x02:"SHF_ALLOC (Occupies memory during execution)", 0x04:"SHF_EXECINSTR (Executable)", 0x10:"SHF_MERGE (Might be merged)",\
	  0x20:"SHF_STRINGS (Null-terminated strings)", 0x40:"SHF_INFO_LINK (\'sh_info\' contains SHT index)", 0x80:"SHF_LINK_ORDER (Preserved order after combining)", 0x100:"SHF_OS_NONCONFORMING (Non-standard OS specific handling required)",\
	  0x200:"SHF_GROUP (Section is member of a group)", 0x400:"SHF_TLS (Section hold thread-local data)", 0x0FF00000:"SHF_MASKOS (OS-specific)", 0xF0000000:"SHF_MASKPROC (Processor-specific)",\
	  0x800:"SHF_COMPRESSED (Compressed)"
	  0x4000000:"SHF_ORDERED (Special ordering requirement (Solaris))", 0x8000000:"SHF_EXCLUDE (Section is excluded unless referenced or allocated (Solaris))"}
	'''
	SH_ADDR 	 = 	0x0C
	SH_ADDR_SZ 	 = 	4

	SH_OFFSET 	 =	0x10
	SH_OFFSET_SZ =  4

	SH_SIZE   	 =  0x14
	SH_SIZE_SZ	 =  4

	SH_LINK 	 =	0x18
	SH_LINK_SZ	 =  4

	SH_INFO		 =  0x1C
	SH_INFO_SZ	 =  4

	SH_ADDRALIGN =  0x20
	SH_ADDRALIGN_SZ = 4

	SH_ENTSIZE =  0x24
	SH_ENTSIZE_SZ = 4

	# 64 bit
	SH_FLAGS64 = 0x08
	SH_FLAGS64_SZ = 8

	SH_ADDR64	 = 	0x10
	SH_ADDR64_SZ 	 = 	8

	SH_OFFSET64 	 =	0x18
	SH_OFFSET64_SZ 	 =  8

	SH_SIZE64   	 =  0x20
	SH_SIZE64_SZ	 =  8

	SH_LINK64 	 =	0x28
	SH_LINK64_SZ	 =  4

	SH_INFO64		 =  0x2C
	SH_INFO64_SZ	 =  4

	SH_ADDRALIGN64 =  0x30
	SH_ADDRALIGN64_SZ = 8

	SH_ENTSIZE64 	=  0x38
	SH_ENTSIZE64_SZ =   8

	def __init__(self, buffer,  sh_idx, shent_off, shent_sz,  opt_64bit, opt_big_endian):
		self.opt_64bit = opt_64bit
		self.opt_big_endian = opt_big_endian
		self.opt_idx = sh_idx
		self.opt_name = ""
		shent_off += (sh_idx*shent_sz)

		if self.opt_64bit:
			self.sh_name_off = buffer[shent_off + SectionHeader.SH_NAME:shent_off + SectionHeader.SH_NAME + SectionHeader.SH_NAME_SZ]
			self.sh_type = buffer[shent_off + SectionHeader.SH_TYPE:shent_off + SectionHeader.SH_TYPE + SectionHeader.SH_TYPE_SZ]
			self.sh_flags = buffer[shent_off + SectionHeader.SH_FLAGS64:shent_off + SectionHeader.SH_FLAGS64 + SectionHeader.SH_FLAGS64_SZ]
			self.sh_addr = buffer[shent_off + SectionHeader.SH_ADDR64:shent_off + SectionHeader.SH_ADDR64 + SectionHeader.SH_ADDR64_SZ]
			self.sh_offset = buffer[shent_off + SectionHeader.SH_OFFSET64:shent_off + SectionHeader.SH_OFFSET64 + SectionHeader.SH_OFFSET64_SZ]
			self.sh_size = buffer[shent_off + SectionHeader.SH_SIZE64:shent_off + SectionHeader.SH_SIZE64 + SectionHeader.SH_SIZE64_SZ]
			self.sh_link = buffer[shent_off + SectionHeader.SH_LINK64:shent_off + SectionHeader.SH_LINK64 + SectionHeader.SH_LINK64_SZ]
			self.sh_info = buffer[shent_off + SectionHeader.SH_INFO64:shent_off + SectionHeader.SH_INFO64 + SectionHeader.SH_INFO64_SZ]
			self.sh_addralign = buffer[shent_off + SectionHeader.SH_ADDRALIGN64:shent_off + SectionHeader.SH_ADDRALIGN64 + SectionHeader.SH_ADDRALIGN64_SZ]
			self.sh_entsize = buffer[shent_off + SectionHeader.SH_ENTSIZE64:shent_off + SectionHeader.SH_ENTSIZE64 + SectionHeader.SH_ENTSIZE64_SZ]
		else:
			self.sh_name_off = buffer[shent_off + SectionHeader.SH_NAME:shent_off + SectionHeader.SH_NAME + SectionHeader.SH_NAME_SZ]
			self.sh_type = buffer[shent_off + SectionHeader.SH_TYPE:shent_off + SectionHeader.SH_TYPE + SectionHeader.SH_TYPE_SZ]
			self.sh_flags = buffer[shent_off + SectionHeader.SH_FLAGS:shent_off + SectionHeader.SH_FLAGS + SectionHeader.SH_FLAGS_SZ]
			self.sh_addr = buffer[shent_off + SectionHeader.SH_ADDR:shent_off + SectionHeader.SH_ADDR + SectionHeader.SH_ADDR_SZ]
			self.sh_offset = buffer[shent_off + SectionHeader.SH_OFFSET:shent_off + SectionHeader.SH_OFFSET + SectionHeader.SH_OFFSET_SZ]
			self.sh_size = buffer[shent_off + SectionHeader.SH_SIZE:shent_off + SectionHeader.SH_SIZE + SectionHeader.SH_SIZE_SZ]
			self.sh_link = buffer[shent_off + SectionHeader.SH_LINK:shent_off + SectionHeader.SH_LINK + SectionHeader.SH_LINK_SZ]
			self.sh_info = buffer[shent_off + SectionHeader.SH_INFO:shent_off + SectionHeader.SH_INFO + SectionHeader.SH_INFO_SZ]
			self.sh_addralign = buffer[shent_off + SectionHeader.SH_ADDRALIGN:shent_off + SectionHeader.SH_ADDRALIGN + SectionHeader.SH_ADDRALIGN_SZ]
			self.sh_entsize = buffer[shent_off + SectionHeader.SH_ENTSIZE:shent_off + SectionHeader.SH_ENTSIZE + SectionHeader.SH_ENTSIZE_SZ]

	def get_name_offset(self):
		"""Get Name Offset
		"""
		return unpack(self.sh_name_off, self.opt_big_endian)

	def get_name(self):
		"""Get Name
		"""
		return self.opt_name

	def get_offset(self):
		"""Get Offset
		"""
		return unpack(self.sh_offset, self.opt_big_endian)

	def get_flags(self):
		"""Get Flags
		"""
		out = ""
		code = unpack(self.sh_flags, self.opt_big_endian)
		for x in SectionHeader.SH_FLAGS_T:
			if (code & x)>0:
				if out !="":
					out+=" + "
				out +=   SectionHeader.SH_FLAGS_T[x]
				code = code & (~x)

		# Unknown code
		if code>0:
			return out + "Unknown"
		return out

	def update_name(self, str_header_offset, buffer):
		"""Update
		"""
		self.opt_name = readstring(buffer, str_header_offset + self.get_name_offset())


	def get_type(self):
		"""Get Type
		"""
		code = unpack(self.sh_type, self.opt_big_endian)
		if code in SectionHeader.SH_TYPE_T:
			return SectionHeader.SH_TYPE_T[code]
		return "Unknown"

	def print_all(self):
		"""Print all
		"""
		log("")
		log("\t[%-s] %s"%(self.opt_idx, self.opt_name))
		log("\t%-50s0x%-20x"%("Name Offset:", unpack(self.sh_name_off, self.opt_big_endian)))
		log("\t%-50s%-20s"%("Type:", self.get_type()))
		log("\t%-50s%-20s"%("Flags:", self.get_flags()))
		log("\t%-50s0x%-20x"%("Virtual Address:", unpack(self.sh_addr, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Physical Address:", unpack(self.sh_offset, self.opt_big_endian)))
		log("\t%-50s%-20d(bytes)"%("Size in File:", unpack(self.sh_size, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Link:", unpack(self.sh_link, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Info:", unpack(self.sh_info, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Align:", unpack(self.sh_addralign, self.opt_big_endian)))
		log("\t%-50s0x%-20x"%("Entry Size:",unpack(self.sh_entsize, self.opt_big_endian)))

class ElfParser:
	"""Elf Parser
	   https://en.wikipedia.org/wiki/Executable_and_Linkable_Format
	   https://docs.oracle.com/cd/E19683-01/816-1386/chapter6-83432/index.html
	"""

	def __init__(self, buffer):
		self.buffer = buffer
		self.elfHeader = ElfHeader(buffer)
		self.programHeaders = []
		self.sectionHeaders = []

		opt_64bit = self.elfHeader.get_opt_64bit()
		opt_big_endian = self.elfHeader.get_opt_bigendian()

		# Collect Program Headers
		phent_off = self.elfHeader.get_ph_offset()
		phent_sz = self.elfHeader.get_phent_size()
		phent_num = self.elfHeader.get_phnum_num()
		for opt_ph_idx in range(phent_num):
			ph = ProgramHeader(buffer, opt_ph_idx, phent_off, phent_sz, opt_64bit, opt_big_endian)
			self.programHeaders.append(ph)

		# Collect Section Headers
		shent_off = self.elfHeader.get_sh_offset()
		shent_sz = self.elfHeader.get_shent_size()
		shent_num = self.elfHeader.get_shnum_num()
		for opt_sh_idx in range(shent_num):
			sh = SectionHeader(buffer, opt_sh_idx, shent_off, shent_sz, opt_64bit, opt_big_endian)
			self.sectionHeaders.append(sh)

		# Update names of sections
		try:
			str_header = self.sectionHeaders[self.elfHeader.get_shstr_ndx()]
			str_entries_offset = str_header.get_offset()

			# String name
			for sh in self.sectionHeaders:
				sh.update_name(str_entries_offset, buffer)
		except Exception as e:
			log(e)

	def print_all(self):
		"""Print all
		"""
		log("################################")
		log("########## ELF HEADER ##########")
		log("################################")
		self.elfHeader.print_all()

		log("#####################################")
		log("########## PROGRAM HEADERS ##########")
		log("#####################################")
		for ph in self.programHeaders:
			ph.print_all()

		log("#####################################")
		log("########## SECTION HEADERS ##########")
		log("#####################################")
		for sh in self.sectionHeaders:
			sh.print_all()

	def modify(self, source, dest):
		# parse program headers
		temp_offset=0
		for pidx in range(0, nm_program_headers):
			# cycle through all the headers
			temp_offset = off_program_headers + sz_entry_program_headers * pidx


			type = struct.unpack("<L", b"".join(original_absfile[temp_offset:temp_offset+4]))[0]
			offset = struct.unpack("<L", b"".join(original_absfile[temp_offset+4:temp_offset+8]))[0]
			virtual_start_address = struct.unpack("<L", b"".join(original_absfile[temp_offset+8:temp_offset+12]))[0]
			physical_start_address = struct.unpack("<L", b"".join(original_absfile[temp_offset+12:temp_offset+16]))[0]
			filesize = struct.unpack("<L", b"".join(original_absfile[temp_offset+16:temp_offset+20]))[0]
			memsize = struct.unpack("<L", b"".join(original_absfile[temp_offset+20:temp_offset+24]))[0]
			flags = struct.unpack("<L", b"".join(original_absfile[temp_offset+24:temp_offset+28]))[0]
			align = struct.unpack("<L", b"".join(original_absfile[temp_offset+28:temp_offset+32]))[0]



			print("PROGRAM_HEADER:"+" "+hex(offset)+" "+hex(physical_start_address)+" "+hex(virtual_start_address)+" "+hex(memsize) + " "+hex(filesize))
			if physical_start_address >= ORIGINAL_LOWEST_ADDRESS and physical_start_address+filesize <= ORIGINAL_HIGHEST_ADDRESS:
				#if filesize != memsize and filesize > 0:
				#print( "Filesize isn't the same as memsize. This case wasn't implemented yet: for example .bss that is being initialized by the programmer")
				#	sys.exit(0)


				# initialized cells
				if filesize > 0:
					segment_starting_offsets.append(offset)
					segment_ending_offsets.append(offset+filesize)
					segment_starting_addresses.append(physical_start_address)
					segment_ending_addresses.append(physical_start_address+filesize)

			elif physical_start_address == COPY_LOWEST_ADDRESS and physical_start_address+filesize == COPY_HIGHEST_ADDRESS:
				OFFSET = offset
				foundCopySegment = True

		if foundCopySegment:
			print( "\n###########  %s Segments to copy ############"%(len(segment_starting_offsets)))
			# clone file in memory
			edited_absfile = original_absfile[:]
					# initialize copy segment to 0xff's
			#edited_absfile[offset:offset+filesize] = [b'\xff'] * filesize

			for idx in range(0,len(segment_starting_offsets)):
				pg_start_offset = segment_starting_offsets[idx]
				pg_end_offset = segment_ending_offsets[idx]
				print ("## -> \toffsets: 0x%x-0x%x\taddresses: 0x%x-0x%x size: %s"%(pg_start_offset,pg_end_offset , segment_starting_addresses[idx], segment_ending_addresses[idx], segment_ending_addresses[idx]-segment_starting_addresses[idx]))

				temp_offset = OFFSET + segment_starting_addresses[idx]	- ORIGINAL_LOWEST_ADDRESS	# calculate destination in the copy segment

				copy_offset = temp_offset
				copy_end = temp_offset+(pg_end_offset-pg_start_offset)
				print( "## Copy to %s - %s %s\n"%(hex(copy_offset), hex(copy_end), pg_end_offset-pg_start_offset))

				edited_absfile[copy_offset:copy_end]=edited_absfile[pg_start_offset:pg_end_offset]



				#print(virtual_start_address)
				#print (virtual_start_address+memsize)
				# This should only be reached if we parse RAM program headers. Interrupt headers go after the COPY Program header
		else:
			log("Nothing to Copy")

	def get_buffer(self):
		return self.buffer

