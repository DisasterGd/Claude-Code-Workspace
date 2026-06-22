#!/usr/bin/env node
/**
 * CapacityConverter CLI — Binary & Decimal Unit Conversion
 *
 * Usage:
 *   node cli.js <value> <fromUnit> <toUnit>          Basic conversion
 *   node cli.js <value> <unit> --all                  Show all equivalents
 *   node cli.js <value> <fromUnit> <toUnit> --json    JSON output
 *   node cli.js --units                               List all supported units
 *   node cli.js --help                                Show help
 *
 * Examples:
 *   node cli.js 5 GiB GB
 *   node cli.js 1 TiB GB --json
 *   node cli.js 1024 MiB --all
 *   node cli.js --units
 */

'use strict';

var converter = require('./converter.js');

// ── Argument Parsing ────────────────────────────────────────────────────────

var args = process.argv.slice(2);

// Parse flags
var flags = {
  all:    args.indexOf('--all')    !== -1,
  json:   args.indexOf('--json')   !== -1,
  units:  args.indexOf('--units')  !== -1,
  help:   args.indexOf('--help')   !== -1 || args.indexOf('-h') !== -1
};

// Remove flags from positional args
var positional = args.filter(function(arg) {
  return !arg.startsWith('--') && arg !== '-h';
});

// ── Help ────────────────────────────────────────────────────────────────────

function showHelp() {
  console.log([
    'CapacityConverter CLI — Binary & Decimal Unit Conversion',
    '',
    'Usage:',
    '  node cli.js <value> <fromUnit> <toUnit>          Basic conversion',
    '  node cli.js <value> <unit> --all                  Show all equivalents',
    '  node cli.js <value> <fromUnit> <toUnit> --json    Machine-readable JSON',
    '  node cli.js --units                               List supported units',
    '  node cli.js --help                                Show this help',
    '',
    'Supported units:',
    '  Binary (IEC):  bit, B, KiB, MiB, GiB, TiB, PiB, EiB    (×1024)',
    '  Decimal (SI):  bit, B, KB, MB, GB, TB, PB, EB          (×1000)',
    '',
    'Examples:',
    '  $ node cli.js 5 GiB GB',
    '  5 GiB = 5.3687 GB',
    '',
    '  $ node cli.js 1 TiB GB --json',
    '  {"value":1,"fromUnit":"TiB","toUnit":"GB","result":1099.5116,"formatted":"1,099.51 GB"}',
    '',
    '  $ node cli.js 1024 MiB --all',
    '  [shows the value in all 16 units]',
    '',
    'Note: 1 KiB = 1024 bytes (binary), 1 KB = 1000 bytes (decimal).',
    '      Memory/storage uses binary; network/HDD marketing uses decimal.'
  ].join('\n'));
}

// ── List Units ──────────────────────────────────────────────────────────────

function listUnits() {
  var units = converter.getUnits();
  var binary  = units.filter(function(u) { return u.family === 'binary'; });
  var decimal = units.filter(function(u) { return u.family === 'decimal'; });

  console.log('IEC Binary Units (powers of 1024):');
  console.log('  ' + binary.map(function(u) {
    return u.key + ' (' + u.label + ') = ' + converter.formatNumber(u.bitsPerUnit) + ' bits';
  }).join('\n  '));

  console.log('\nSI Decimal Units (powers of 1000):');
  console.log('  ' + decimal.map(function(u) {
    return u.key + ' (' + u.label + ') = ' + converter.formatNumber(u.bitsPerUnit) + ' bits';
  }).join('\n  '));
}

// ── Convert ─────────────────────────────────────────────────────────────────

function doConvert(valueStr, fromUnit, toUnit) {
  var validation = converter.validate(valueStr);
  if (!validation.valid) {
    console.error('Error: ' + validation.error);
    process.exit(1);
  }

  var value = validation.sanitized;

  // Validate units
  var allUnits = converter.getUnits().map(function(u) { return u.key; });
  if (allUnits.indexOf(fromUnit) === -1) {
    console.error('Error: Unknown unit "' + fromUnit + '". Use --units to list supported units.');
    process.exit(1);
  }
  if (allUnits.indexOf(toUnit) === -1) {
    console.error('Error: Unknown unit "' + toUnit + '". Use --units to list supported units.');
    process.exit(1);
  }

  try {
    return converter.convert(value, fromUnit, toUnit);
  } catch (e) {
    console.error('Error: ' + e.message);
    process.exit(1);
  }
}

function showAll(valueStr, unit) {
  var validation = converter.validate(valueStr);
  if (!validation.valid) {
    console.error('Error: ' + validation.error);
    process.exit(1);
  }

  var allUnits = converter.getUnits().map(function(u) { return u.key; });
  if (allUnits.indexOf(unit) === -1) {
    console.error('Error: Unknown unit "' + unit + '". Use --units to list supported units.');
    process.exit(1);
  }

  var equivalents = converter.getEquivalents(validation.sanitized, unit);

  console.log(converter.formatNumber(validation.sanitized) + ' ' + unit + ' equals:\n');

  console.log('  [IEC Binary — powers of 1024]');
  Object.keys(equivalents.binary).forEach(function(key) {
    var e = equivalents.binary[key];
    console.log('    ' + key + ': ' + e.formattedResult);
  });

  console.log('\n  [SI Decimal — powers of 1000]');
  Object.keys(equivalents.decimal).forEach(function(key) {
    var e = equivalents.decimal[key];
    console.log('    ' + key + ': ' + e.formattedResult);
  });
}

// ── Main ────────────────────────────────────────────────────────────────────

function main() {
  if (flags.help) {
    showHelp();
    return;
  }

  if (flags.units) {
    listUnits();
    return;
  }

  if (flags.all) {
    if (positional.length < 2) {
      console.error('Error: --all requires <value> <unit>. E.g.: node cli.js 1024 MiB --all');
      process.exit(1);
    }
    showAll(positional[0], positional[1]);
    return;
  }

  // Standard conversion: <value> <fromUnit> <toUnit>
  if (positional.length < 3) {
    console.error('Error: Expected <value> <fromUnit> <toUnit>. Use --help for usage.');
    process.exit(1);
  }

  var result = doConvert(positional[0], positional[1], positional[2]);

  if (flags.json) {
    console.log(JSON.stringify({
      value:     converter.validate(positional[0]).sanitized,
      fromUnit:  positional[1],
      toUnit:    positional[2],
      result:    result.result,
      formatted: result.formattedResult,
      formula:   result.formula
    }));
  } else {
    console.log(result.formula);
  }
}

main();
