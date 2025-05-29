// src/lib/filterUtils.js
export function shouldShow(filter, type, level) {
  if (!filter || filter === 'TCIV') return true;
  const filterUpper = filter.toUpperCase();
  const typeUpper = type.toUpperCase().charAt(0);
  const parsedLevel = parseInt(level, 10);
  if (isNaN(parsedLevel)) return false;

  let i = 0;
  while (i < filterUpper.length) {
    const char = filterUpper[i];
    if (['T', 'C', 'I', 'V'].includes(char)) {
      let currentType = char;
      let levels = '';
      i++;
      while (i < filterUpper.length && !isNaN(parseInt(filterUpper[i], 10))) {
        levels += filterUpper[i];
        i++;
      }
      if (currentType === typeUpper) {
        if (levels === '') return true;
        if (levels.includes(parsedLevel.toString())) return true;
      }
    } else {
      i++;
    }
  }
  return false;
}
