# ⚡ Binary Capacity Converter

二进制容量换算工具 — Convert between IEC binary units (KiB, MiB, GiB…) and SI decimal units (KB, MB, GB…) with a clean web UI or command line.

## Quick Start

### Web App
Open `index.html` in any modern browser. No build step, no dependencies.

```bash
start index.html    # Windows
open index.html     # macOS
xdg-open index.html # Linux
```

### CLI
```bash
# Basic conversion
node cli.js 5 GiB GB
# → 5 GiB × 8,589,934,592 bits/GiB ÷ 8,000,000,000 bits/GB = 5.3687 GB

# Show all 16 unit equivalents
node cli.js 1024 MiB --all

# Machine-readable JSON
node cli.js 1 TiB GB --json

# List all supported units
node cli.js --units
```

## Supported Units

| Family | Units | Formula |
|--------|-------|---------|
| **IEC Binary** | bit, B, KiB, MiB, GiB, TiB, PiB, EiB | 1 KiB = 1024 B |
| **SI Decimal** | bit, B, KB, MB, GB, TB, PB, EB | 1 KB = 1000 B |

## Unit Reference

### IEC Binary (powers of 1024)

| Unit | Abbr | Bytes | Bits |
|------|------|-------|------|
| Bit | bit | ¹⁄₈ | 1 |
| Byte | B | 1 | 8 |
| Kibibyte | KiB | 1,024 | 8,192 |
| Mebibyte | MiB | 1,048,576 | 8,388,608 |
| Gibibyte | GiB | 1,073,741,824 | 8,589,934,592 |
| Tebibyte | TiB | 1,099,511,627,776 | 8,796,093,022,208 |
| Pebibyte | PiB | 1,125,899,906,842,624 | 9,007,199,254,740,992 |
| Exbibyte | EiB | 1,152,921,504,606,846,976 | 9,223,372,036,854,775,808 |

### SI Decimal (powers of 1000)

| Unit | Abbr | Bytes | Bits |
|------|------|-------|------|
| Kilobyte | KB | 1,000 | 8,000 |
| Megabyte | MB | 1,000,000 | 8,000,000 |
| Gigabyte | GB | 1,000,000,000 | 8,000,000,000 |
| Terabyte | TB | 1,000,000,000,000 | 8,000,000,000,000 |
| Petabyte | PB | 1,000,000,000,000,000 | 8,000,000,000,000,000 |
| Exabyte | EB | 1,000,000,000,000,000,000 | 8,000,000,000,000,000,000 |

## Features

- **Real-time conversion** — type in either field, the other updates instantly (150ms debounce)
- **Bidirectional editing** — edit the output field to reverse the conversion direction
- **Formula display** — see the exact math: `5 GiB × 8,589,934,592 ÷ 8,000,000,000 = 5.3687 GB`
- **All equivalents** — view the value in all 16 units at a glance (binary column + decimal column)
- **Copy to clipboard** — copy the formula or any individual equivalent with one click
- **Dark / Light theme** — system-preference-aware with manual toggle, persisted to localStorage
- **Keyboard shortcut** — `Ctrl+Shift+S` or `Ctrl+Shift+X` to swap units
- **Responsive** — works on mobile, tablet, and desktop
- **Smart input** — strips commas, handles scientific notation, validates sanely
- **Reference table** — collapsible unit reference built into the UI
- **CLI mode** — use from the terminal with `--json` for scripting

## File Structure

```
├── converter.js    # Core library (UMD — works in browser & Node.js)
├── index.html      # Web app (HTML + CSS + JS, zero dependencies)
├── cli.js          # Node.js CLI wrapper
└── README.md       # This file
```

## API (`converter.js`)

```js
var CV = CapacityConverter;

// Convert between units
CV.convert(5, 'GiB', 'GB');
// → { result: 5.36870912, formattedResult: '5.3687 GB', formula: '5 GiB × ... = 5.3687 GB' }

// Get all supported units
CV.getUnits();
// → [{ key: 'GiB', label: 'Gibibyte (GiB)', family: 'binary', bitsPerUnit: 8589934592 }, ...]

// Get all equivalents
CV.getEquivalents(5, 'GiB');
// → { binary: { bit: {...}, B: {...}, KiB: {...}, ... }, decimal: { ... } }

// Format a number with magnitude-based precision
CV.formatNumber(5368.70912);
// → '5,368.71'

// Validate user input
CV.validate('1,500.5');
// → { valid: true, sanitized: 1500.5, error: null }
CV.validate('-5');
// → { valid: false, sanitized: null, error: 'Capacity cannot be negative' }
```

## Why Binary vs Decimal?

- **IEC Binary** (KiB, MiB, GiB): Used by operating systems (Windows, Linux, macOS), RAM, and CPU caches. Based on powers of 2 — natural for computers.
- **SI Decimal** (KB, MB, GB): Used by hard drive manufacturers, network speeds, and the metric system. Based on powers of 10 — natural for humans.

A "1 TB" hard drive is actually ~931 GiB in your OS. This tool helps you see exactly why.

## Browser Compatibility

All modern browsers (Chrome, Firefox, Safari, Edge). Requires ES5+ (no transpilation needed).

## License

MIT
