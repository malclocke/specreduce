# Order of ops is:
# - Dark subtract
# - Vertical crop
# - Bin
# - Calibrate
# - Wavelength crop
# - Normalise
#

SCRIPT_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

DARK_SUBTRACTED_DIR			:= dark_subtracted
VCROP_DIR								:= vcropped
BINNED_DIR							:= binned
CALIBRATED_DIR					:= calibrated
WAVELENGTH_CROPPED_DIR	:= wavelength_cropped
NORMALISED_DIR					:= normalised
REDUCED_DIR							:= reduced

VPADDING								:= 10

PATTERN ?= *_[0-9][0-9][0-9][0-9].fit

DARK_SUBTRACTED_TARGETS := $(patsubst %.fit, $(DARK_SUBTRACTED_DIR)/%.fit, $(wildcard $(PATTERN)))
VCROP_TARGETS := $(patsubst %.fit, $(VCROP_DIR)/%.fit, $(wildcard $(PATTERN)))
BINNED_TARGETS := $(patsubst %.fit, $(BINNED_DIR)/%.fit, $(wildcard $(PATTERN)))
CALIBRATED_TARGETS := $(patsubst %.fit, $(CALIBRATED_DIR)/%.fit, $(wildcard $(PATTERN)))
WAVELENGTH_CROPPED_TARGETS := $(patsubst %.fit, $(WAVELENGTH_CROPPED_DIR)/%.fit, $(wildcard $(PATTERN)))
NORMALISED_TARGETS := $(patsubst %.fit, $(NORMALISED_DIR)/%.fit, $(wildcard $(PATTERN)))
REDUCED_TARGETS := $(patsubst %.fit, $(REDUCED_DIR)/%.fit, $(wildcard $(PATTERN)))

all: reduced

dark_subtract: $(DARK_SUBTRACTED_TARGETS)
vcrop: $(VCROP_TARGETS)
binned: $(BINNED_TARGETS)
calibrated: $(CALIBRATED_TARGETS)
wavelength_cropped: $(WAVELENGTH_CROPPED_TARGETS)
normalised: $(NORMALISED_TARGETS)
reduced: $(REDUCED_TARGETS)

clean:
	rm -f $(DARK_SUBTRACTED_DIR)/* $(VCROP_DIR)/* $(CALIBRATED_DIR)/* \
		$(WAVELENGTH_CROPPED_DIR)/* $(NORMALISED_DIR)/* $(REDUCED_DIR)/*

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

$(BINNED_DIR)/%.fit: $(VCROP_DIR)/%.fit
	mkdir -p $(BINNED_DIR)
	$(SCRIPT_DIR)/bin.py --outfile $@ $<

$(CALIBRATED_DIR)/%.fit: $(BINNED_DIR)/%.fit
	mkdir -p $(CALIBRATED_DIR)
ifdef MAXX
	$(SCRIPT_DIR)/auto_calibrate.py --maxx $(MAXX) --spacing $(SPACING) --outfile $@ $<
else
	$(SCRIPT_DIR)/auto_calibrate.py --spacing $(SPACING) --outfile $@ $<
endif

$(WAVELENGTH_CROPPED_DIR)/%.fit: $(CALIBRATED_DIR)/%.fit
	mkdir -p $(WAVELENGTH_CROPPED_DIR)
	$(SCRIPT_DIR)/wavelength_crop.py --outfile $@ $<

$(NORMALISED_DIR)/%.fit: $(WAVELENGTH_CROPPED_DIR)/%.fit
	mkdir -p $(NORMALISED_DIR)
	$(SCRIPT_DIR)/normalise.py --outfile $@ $<

$(REDUCED_DIR)/%.fit: $(NORMALISED_DIR)/%.fit
	mkdir -p $(REDUCED_DIR)
	cp $< $@ 
