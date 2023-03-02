THISDIR = $(dir $(abspath $(firstword $(MAKEFILE_LIST))))

SOURCE ?= ${THISDIR}
TMP_FILELIST = ${wildcard ${SOURCE}/*.mp4}
TMP_FILELIST = $(shell echo "${wildcard ${SOURCE}/*.mp4}" | sed 's/ /\!TM_/g')
FILELIST = $(shell echo "${TMP_FILELIST}" |sed 's/mp4\!TM_/mp4 /g')

all: ${FILELIST}
	@echo "end"
#	@echo "${FILELIST}"

%.mp4: STARTM
#	@echo $(shell echo ${@} | sed 's/\!TM_/ /g')
	python3.7 translation_video.py --source "${@}"

STARTM:
	@echo "Start"