# Order of ops is:
# - Dark subtract
# - Vertical crop
# - Calibrate and bin
# - Horizontal crop
# - Normalise
#

SCRIPT_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

DARK_SUBTRACTED_DIR	:= dark_subtracted
VCROP_DIR						:= vcropped
CALIBRATED_DIR			:= calibrated
HCROP_DIR						:= hcropped
NORMALISED_DIR			:= normalised
REDUCED_DIR					:= reduced
VPADDING						:= 10

PATTERN ?= *_[0-9][0-9][0-9][0-9].fit

TARGETS := $(patsubst %.fit, $(REDUCED_DIR)/%.fit, $(wildcard $(PATTERN)))

all: $(TARGETS)

clean:
	rm -f $(DARK_SUBTRACTED_DIR)/* $(VCROP_DIR)/* $(CALIBRATED_DIR)/* \
		$(HCROP_DIR)/* $(NORMALISED_DIR)/* $(REDUCED_DIR)/*

$(DARK_SUBTRACTED_DIR)/%.fit: %.fit
	mkdir -p $(DARK_SUBTRACTED_DIR)
ifdef DARK
		$(SCRIPT_DIR)/dark_subtract.py --outfile $@ $(DARK) $<
else
		cp -v $< $@
endif

$(VCROP_DIR)/%.fit: $(DARK_SUBTRACTED_DIR)/%.fit
	mkdir -p $(VCROP_DIR)
	$(SCRIPT_DIR)/autocrop.py --filterfactor 0.95 --padding $(VPADDING) --outfile $@ $<

$(CALIBRATED_DIR)/%.fit: $(VCROP_DIR)/%.fit
	mkdir -p $(CALIBRATED_DIR)
ifdef MAXX
	$(SCRIPT_DIR)/auto_calibrate.py --maxx $(MAXX) --spacing $(SPACING) --outfile $@ $<
else
	$(SCRIPT_DIR)/auto_calibrate.py --spacing $(SPACING) --outfile $@ $<
endif

$(HCROP_DIR)/%.fit: $(CALIBRATED_DIR)/%.fit
	mkdir -p $(HCROP_DIR)
	$(SCRIPT_DIR)/wavelength_crop.py --outfile $@ $<

$(NORMALISED_DIR)/%.fit: $(HCROP_DIR)/%.fit
	mkdir -p $(NORMALISED_DIR)
	$(SCRIPT_DIR)/normalise.py --outfile $@ $<

$(REDUCED_DIR)/%.fit: $(NORMALISED_DIR)/%.fit
	mkdir -p $(REDUCED_DIR)
	cp $< $@ 
