// Common javascript utilities

// custom

const getPercentChange = (start, end) => {
  if (start > 0 && end > 0) {
    const pctChange = (end - start) / start * 100;
    const sign = pctChange >= 0 ? '+' : '';
    return `${sign}${pctChange.toFixed(1)}%`
  } else {
    const change = end - start;
    const sign = change >= 0 ? '+' : '';
    return `${sign}\$${change.toFixed(0)}`
  }
}


//  sleep utility

const sleep = (sec) => {
  return new Promise(resolve => setTimeout(resolve, sec * 1000));
};


// array utilities

const sum = (arr) => arr.reduce((a, b) => a + b, 0);

const removeDuplcates = (arr) => [...new Set(arr)]

const sortNumericArr = (arr) => arr.sort((a, b) => a - b);

const getPosition = (sortedArr, target) => {
  for (let i = 0; i < sortedArr.length; i++) {
    if (target <= sortedArr[i]) {
      return i;
    }
  }
  return sortedArr.length;
};


// date time utilities

const HOUR_SIZE = 3600;
const DAY_SIZE = 86400;

const getEpochTime = () => Date.now() / 1000;

const epochTimeToDate = (epochTimestamp) => {
  return new Date(epochTimestamp * 1000);
};

const dateToEpoch = (date) => {
  return new Date(date).getTime() / 1000;
}

const formatDate = (date, type) => {
  // type: date, dateWithYear, textDate, time, weekday
  if (type == undefined) {
    // 3/3/2023, 11:36:24 AM
    return date.toLocaleString('en-US');
  } else if (type === 'date') {
    // 3/3
    return date.toLocaleString('en-US', { month: 'numeric', day: 'numeric' });
  } else if (type === 'dateWithYear') {
    // 3/3/2023
    return date.toLocaleString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' });
  } else if (type === 'textDate') {
    // Mar 3
    return date.toLocaleString('en-US', { month: 'short', day: 'numeric' });
  } else if (type === 'time') {
    // 11:36 AM
    return date.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric' });
  } else if (type === 'weekday') {
    // Fri
    return date.toLocaleString('en-US', { weekday: 'short' });
  } else {
    return date.toLocaleString('en-US');
  }
};
