// Elite Clean Pro — Quote calculator
// Listens to bedroom, frequency, and property radios anywhere on the page.

document.addEventListener('DOMContentLoaded', function () {
  var priceEl = document.getElementById('quote-price');
  var detailEl = document.getElementById('quote-detail');
  if (!priceEl) return;

  var basePrices = {
    house:  { '1': 139, '2': 159, '3': 179, '4': 199, '5': 219 },
    condo:  { '1': 119, '2': 139, '3': 159, '4': 179, '5': 199 },
    office: { '1': 800, '2': 1100, '3': 1400, '4': 1700, '5': 2000 }
  };
  var freqMult  = { onetime: 1.0,  weekly: 0.85, biweekly: 0.90, monthly: 0.95 };
  var freqLabel = { onetime: 'one-time', weekly: 'weekly', biweekly: 'bi-weekly', monthly: 'monthly' };

  function getVal(name, fallback) {
    var el = document.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : fallback;
  }

  function update() {
    var prop = getVal('property', 'house');
    var bed  = getVal('bedrooms', '1');
    var freq = getVal('frequency', 'onetime');

    var base = (basePrices[prop] && basePrices[prop][bed]) || basePrices.house[bed] || 139;
    var price = Math.round(base * (freqMult[freq] || 1));

    priceEl.textContent = price;

    var propLabel = prop === 'office' ? 'office' : (prop === 'condo' ? 'condo' : 'home');
    var bedLabel  = bed === '5' ? '5+ bedroom' : bed + '-bedroom';
    var period    = prop === 'office' ? '/month' : '/visit';

    var periodEl = document.querySelector('.quote-period');
    if (periodEl) periodEl.textContent = period;

    if (detailEl) {
      detailEl.textContent = bedLabel + ' ' + propLabel + ' \u00B7 ' +
        (freqLabel[freq] || freq) + ' \u00B7 includes 100-point checklist inspection';
    }
  }

  var inputs = document.querySelectorAll(
    'input[name="bedrooms"], input[name="frequency"], input[name="property"]'
  );
  inputs.forEach(function (input) {
    input.addEventListener('change', update);
  });

  update();
});
