# Order of ops is:
# - Dark subtract - TBD
# - Vertical crop
# - Calibrate and bin
# - Horizontal crop
# - Stack
#
SPECTRAPLOT_DIR := /home/malc/astro/spectraplot

DARK_SUBTRACTED_DIR	:= dark_subtracted
VCROP_DIR						:= vcropped
CALIBRATED_DIR			:= calibrated
HCROP_DIR						:= hcropped

PATTERN ?= *_[0-9][0-9][0-9][0-9].fit

TARGETS := $(patsubst %.fit, hcropped/%.fit, $(wildcard $(PATTERN)))

all: $(TARGETS)

clean:
	rm -f $(DARK_SUBTRACTED_DIR)/* $(VCROP_DIR)/* $(CALIBRATED_DIR)/* \
		$(HCROP_DIR)/*

dark_subtracted/%.fit: %.fit
	$(SPECTRAPLOT_DIR)/dark_subtract.py --outfile $@ $(DARK) $<

vcropped/%.fit: dark_subtracted/%.fit
	$(SPECTRAPLOT_DIR)/autocrop.py --outfile $@ $<

calibrated/%.fit: vcropped/%.fit
	$(SPECTRAPLOT_DIR)/auto_calibrate.py --spacing $(SPACING) --outfile $@ $<

hcropped/%.fit: calibrated/%.fit
	$(SPECTRAPLOT_DIR)/wavelength_crop.py --outfile $@ $<
