F77 := $(shell command -v f77 2> /dev/null)
GFORTRAN := $(shell command -v gfortran 2> /dev/null)
ifndef F77
ifdef GFORTRAN
    ## F77 cannot be found, but gfortran can? Set FC to gfortran
    FC := $(GFORTRAN)
endif
endif

all: pythia_lhe

fc:
	@echo "F77, $(F77)"
	@echo "FC, $(FC)"
	@echo "GFORTRAN, $(GFORTRAN)"

tarball:
	tar czvf pythia.tar.gz pythia_lhe.f pythia-6.4.27.f Makefile

pythia_lhe:
	$(FC) -o pythia_lhe pythia_lhe.f pythia-6.4.27.f 

test:
	cp ../../inputFiles/slha/compressedSpec.slha fort.61
	pythia_lhe < ../../etc/pythia_test.card | tee out.log

clean:
	rm -f pythia_lhe
