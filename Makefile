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
NORMALISED_DIR			:= normalised
VPADDING						:= 10

PATTERN ?= *_[0-9][0-9][0-9][0-9].fit

TARGETS := $(patsubst %.fit, normalised/%.fit, $(wildcard $(PATTERN)))

all: $(TARGETS)

clean:
	rm -f $(DARK_SUBTRACTED_DIR)/* $(VCROP_DIR)/* $(CALIBRATED_DIR)/* \
		$(HCROP_DIR)/* $(NORMALISED_DIR)/*

dark_subtracted/%.fit: %.fit
	mkdir -p dark_subtracted
ifndef $(DARK)
		cp -v $< $@
else
		$(SPECTRAPLOT_DIR)/dark_subtract.py --outfile $@ $(DARK) $<
endif

vcropped/%.fit: dark_subtracted/%.fit
	mkdir -p vcropped
	$(SPECTRAPLOT_DIR)/autocrop.py --filterfactor 0.95 --padding $(VPADDING) --outfile $@ $<

calibrated/%.fit: vcropped/%.fit
	mkdir -p calibrated
	$(SPECTRAPLOT_DIR)/auto_calibrate.py --spacing $(SPACING) --outfile $@ $<

hcropped/%.fit: calibrated/%.fit
	mkdir -p hcropped
	$(SPECTRAPLOT_DIR)/wavelength_crop.py --outfile $@ $<

normalised/%.fit: hcropped/%.fit
	mkdir -p normalised
	$(SPECTRAPLOT_DIR)/normalise.py --outfile $@ $<
