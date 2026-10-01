export const money = value =>
  `৳${Number(value || 0).toLocaleString('en-BD', {minimumFractionDigits: 2})}`;

export const displayDate = value =>
  value ? new Intl.DateTimeFormat('en-BD', {dateStyle: 'medium'}).format(new Date(value)) : '—';

