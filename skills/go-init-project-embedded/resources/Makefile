BINARY         := app
BUILD          := build
TOOLCHAIN_DIR  := toolchain
TINYGO_URL     := https://github.com/helvionics/tinygo/releases/download
TINYGO_VERSION := 0.42.0-dev-9f07d506
TINYGO         := $(TOOLCHAIN_DIR)/tinygo/bin/tinygo
TARGET         := pico

GOOPTS := -size=full \
          -opt=s \
          -panic=trap \
          -gc=conservative \
          -scheduler=tasks

.PHONY: all build test lint vet clean install-toolchain test-toolchain

all: build

# ── Toolchain Management ──────────────────────────────────────────────────────

test-toolchain:
	@if [ -f $(TINYGO) ]; then \
		$(TINYGO) version; \
	else \
		echo "TinyGo toolchain not found at $(TINYGO). Run 'make install-toolchain' first."; \
		exit 1; \
	fi

install-toolchain:
	mkdir -p $(TOOLCHAIN_DIR)
	curl -L $(TINYGO_URL)/v$(TINYGO_VERSION)/tinygo$(TINYGO_VERSION).linux-amd64.tar.gz | tar -xzC $(TOOLCHAIN_DIR)

# ── Build, Test, Lint ──────────────────────────────────────────────────────────

build: test-toolchain | $(BUILD)
	$(TINYGO) build $(GOOPTS) -target=$(TARGET) -o $(BUILD)/$(BINARY).elf ./src

test:
	go test -v ./src/...

lint: vet

vet:
	go vet ./src/...

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
