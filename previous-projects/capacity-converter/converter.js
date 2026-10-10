/**
 * CapacityConverter — Binary & Decimal Capacity Unit Conversion Library
 *
 * Supports 16 units across two families:
 *   IEC (binary):  bit, B, KiB, MiB, GiB, TiB, PiB, EiB  (powers of 1024)
 *   SI  (decimal): bit, B, KB, MB, GB, TB, PB, EB        (powers of 1000)
 *
 * All conversions pass through a canonical "bits" intermediate for correctness
 * and easy extensibility. The library is a UMD module — it works in browsers
 * (window.CapacityConverter) and Node.js (require('./converter.js')).
 *
 * Precision: uses JavaScript Number (IEEE 754 float64). This gives ~15 significant
 * decimal digits, which is more than adequate for all practical capacity values
 * (1 EiB = ~9.22×10¹⁸ bits, still representable with ~16 sig-figs).
 */
(function(root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.CapacityConverter = factory();
  }
}(typeof self !== 'undefined' ? self : this, function() {
  'use strict';

  // ─── Unit Definitions ───────────────────────────────────────────────────
  // Every unit has:
  //   bitsPerUnit : Number — exact count of bits in one unit of this type
  //   base        : 2 | 10 — the multiplier base (1024 or 1000)
  //   family      : 'binary' | 'decimal'
  //   label       : Human-readable name
  //   byteBased   : true for byte-multiple units, false for bit-based

  var UNITS = {
    // ── Base units (shared by both families) ──
    'bit':  { bitsPerUnit: 1,                     base: 2,  family: 'binary',  label: 'Bit',            byteBased: false },
    'B':    { bitsPerUnit: 8,                     base: 2,  family: 'binary',  label: 'Byte',           byteBased: true  },

    // ── IEC Binary units (powers of 1024) ──
    'KiB':  { bitsPerUnit: 8 * 1024,              base: 2,  family: 'binary',  label: 'Kibibyte',       byteBased: true  },
    'MiB':  { bitsPerUnit: 8 * 1024 * 1024,       base: 2,  family: 'binary',  label: 'Mebibyte',       byteBased: true  },
    'GiB':  { bitsPerUnit: 8 * 1024 * 1024 * 1024,base: 2,  family: 'binary',  label: 'Gibibyte',       byteBased: true  },
    'TiB':  { bitsPerUnit: 8 * Math.pow(1024, 4), base: 2,  family: 'binary',  label: 'Tebibyte',       byteBased: true  },
    'PiB':  { bitsPerUnit: 8 * Math.pow(1024, 5), base: 2,  family: 'binary',  label: 'Pebibyte',       byteBased: true  },
    'EiB':  { bitsPerUnit: 8 * Math.pow(1024, 6), base: 2,  family: 'binary',  label: 'Exbibyte',       byteBased: true  },

    // ── SI Decimal units (powers of 1000) ──
    'KB':   { bitsPerUnit: 8 * 1000,              base: 10, family: 'decimal', label: 'Kilobyte',       byteBased: true  },
    'MB':   { bitsPerUnit: 8 * 1000 * 1000,       base: 10, family: 'decimal', label: 'Megabyte',       byteBased: true  },
    'GB':   { bitsPerUnit: 8 * 1000 * 1000 * 1000,base: 10, family: 'decimal', label: 'Gigabyte',       byteBased: true  },
    'TB':   { bitsPerUnit: 8 * Math.pow(1000, 4), base: 10, family: 'decimal', label: 'Terabyte',       byteBased: true  },
    'PB':   { bitsPerUnit: 8 * Math.pow(1000, 5), base: 10, family: 'decimal', label: 'Petabyte',       byteBased: true  },
    'EB':   { bitsPerUnit: 8 * Math.pow(1000, 6), base: 10, family: 'decimal', label: 'Exabyte',        byteBased: true  }
  };

  // ─── Internal Helpers ────────────────────────────────────────────────────

  /**
   * Check if a number is effectively an integer (within floating-point tolerance).
   */
  function isEffectivelyInteger(n) {
    return Math.abs(n - Math.round(n)) < 1e-12;
  }

  /**
   * Format a number with thousand separators and locale-aware grouping.
   * Falls back to a simple regex approach that works everywhere.
   */
  function addThousandSeparators(intPart) {
    // Insert commas every 3 digits from the right
    return intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  // ─── Public API ─────────────────────────────────────────────────────────

  /**
   * Convert a numeric value from one unit to another.
   *
   * @param {number} value    - The numeric value to convert.
   * @param {string} fromUnit - Source unit key (e.g. 'GiB').
   * @param {string} toUnit   - Target unit key (e.g. 'GB').
   * @returns {{ result: number, formattedResult: string, formula: string }}
   */
  function convert(value, fromUnit, toUnit) {
    var fromDef = UNITS[fromUnit];
    var toDef   = UNITS[toUnit];

    if (!fromDef || !toDef) {
      throw new Error('Unknown unit: ' + (!fromDef ? fromUnit : toUnit));
    }

    var bitsValue = value * fromDef.bitsPerUnit;
    var result    = bitsValue / toDef.bitsPerUnit;

    var formattedResult = formatNumber(result);
    var formattedValue  = formatNumber(value);
    var fromBitsFormatted = formatNumber(fromDef.bitsPerUnit);
    var toBitsFormatted   = formatNumber(toDef.bitsPerUnit);

    // Build formula string
    var formula;
    if (fromUnit === toUnit) {
      formula = formattedValue + ' ' + fromUnit + ' = ' + formattedResult + ' ' + toUnit;
    } else {
      formula = formattedValue + ' ' + fromUnit
              + ' × ' + fromBitsFormatted + ' bits/' + fromUnit
              + ' ÷ ' + toBitsFormatted   + ' bits/' + toUnit
              + ' = ' + formattedResult + ' ' + toUnit;
    }

    return {
      result:          result,
      formattedResult: formattedResult + ' ' + toUnit,
      formula:         formula
    };
  }

  /**
   * Return the list of all supported units with their metadata.
   *
   * @returns {Array<{ key: string, label: string, family: string, bitsPerUnit: number }>}
   */
  function getUnits() {
    return Object.keys(UNITS).map(function(key) {
      var def = UNITS[key];
      return {
        key:          key,
        label:        def.label + ' (' + key + ')',
        family:       def.family,
        base:         def.base,
        bitsPerUnit:  def.bitsPerUnit,
        byteBased:    def.byteBased
      };
    });
  }

  /**
   * Get a value expressed in ALL supported units, grouped by family.
   *
   * @param {number} value - The numeric value.
   * @param {string} unit  - The unit of the input value.
   * @returns {{ binary: Object, decimal: Object }}
   */
  function getEquivalents(value, unit) {
    var binary  = {};
    var decimal = {};

    Object.keys(UNITS).forEach(function(key) {
      var def = UNITS[key];
      try {
        var conv = convert(value, unit, key);
        if (def.family === 'binary') {
          binary[key] = conv;
        } else {
          decimal[key] = conv;
        }
      } catch (e) {
        // Should not happen since we validate keys, but be defensive
      }
    });

    return { binary: binary, decimal: decimal };
  }

  /**
   * Format a number according to magnitude-based precision rules.
   *
   * Rules:
   *   - Effectively integer     → no decimal places
   *   - n >= 1000               → 2 decimal places
   *   - 1 <= n < 1000           → 4 decimal places
   *   - 0.001 <= n < 1          → 6 significant figures
   *   - 0 < n < 0.001           → 8 significant figures
   *   - n === 0                 → "0"
   *
   * @param {number} n - The number to format.
   * @returns {string}
   */
  function formatNumber(n) {
    if (n === 0 || isNaN(n) || !isFinite(n)) {
      return n === 0 ? '0' : String(n);
    }

    var absN = Math.abs(n);
    var formatted;

    if (isEffectivelyInteger(n)) {
      formatted = String(Math.round(n));
    } else if (absN >= 1000) {
      formatted = n.toFixed(2);
    } else if (absN >= 1) {
      formatted = n.toFixed(4);
    } else if (absN >= 0.001) {
      formatted = n.toPrecision(6);
    } else {
      formatted = n.toPrecision(8);
    }

    // Separate scientific notation suffix (e.g., "e-10") before cleanup
    var suffix = '';
    var eIdx = formatted.indexOf('e');
    if (eIdx !== -1) {
      suffix = formatted.slice(eIdx);
      formatted = formatted.slice(0, eIdx);
    }

    // Remove trailing zeros after decimal point, but keep at least one digit
    // e.g., "5.20" → "5.2", but "5.00" → "5.0" → "5"
    if (formatted.indexOf('.') !== -1) {
      formatted = formatted.replace(/\.?0+$/, '');
    }

    // Add thousand separators to the integer part
    var parts = formatted.split('.');
    parts[0] = addThousandSeparators(parts[0]);
    formatted = parts.join('.');

    // Reattach scientific notation suffix
    formatted += suffix;

    return formatted;
  }

  /**
   * Validate and sanitize user input.
   *
   * Handles:
   *   - Empty input
   *   - Negative numbers (rejected)
   *   - Commas and spaces (stripped)
   *   - Scientific notation (e.g. "1.5e6")
   *   - Non-numeric garbage
   *
   * @param {string} raw - Raw input string.
   * @returns {{ valid: boolean, sanitized: number|null, error: string|null }}
   */
  function validate(raw) {
    if (raw === null || raw === undefined) {
      return { valid: false, sanitized: null, error: 'Enter a numeric value' };
    }

    // Strip commas, spaces, and non-breaking spaces
    var cleaned = raw.replace(/[,  ]/g, '').trim();

    if (cleaned === '') {
      return { valid: false, sanitized: null, error: 'Enter a numeric value' };
    }

    // Check for valid numeric pattern after cleaning
    // Allows: integers, decimals, scientific notation
    if (!/^-?\d+(\.\d+)?(e[+-]?\d+)?$/i.test(cleaned)) {
      return { valid: false, sanitized: null, error: 'Enter a numeric value' };
    }

    var num = Number(cleaned);

    if (isNaN(num) || !isFinite(num)) {
      return { valid: false, sanitized: null, error: 'Enter a numeric value' };
    }

    if (num < 0) {
      return { valid: false, sanitized: null, error: 'Capacity cannot be negative' };
    }

    return { valid: true, sanitized: num, error: null };
  }

  // ─── Exports ─────────────────────────────────────────────────────────────
  return {
    convert:        convert,
    getUnits:       getUnits,
    getEquivalents: getEquivalents,
    formatNumber:   formatNumber,
    validate:       validate,
    // Expose unit definitions for advanced use
    UNITS:          UNITS
  };
}));
