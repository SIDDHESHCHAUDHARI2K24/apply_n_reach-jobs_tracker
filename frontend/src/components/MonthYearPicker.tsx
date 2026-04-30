import React, { useMemo } from 'react'

interface MonthYearPickerProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const MONTHS = [
  { value: '01', label: 'Jan' },
  { value: '02', label: 'Feb' },
  { value: '03', label: 'Mar' },
  { value: '04', label: 'Apr' },
  { value: '05', label: 'May' },
  { value: '06', label: 'Jun' },
  { value: '07', label: 'Jul' },
  { value: '08', label: 'Aug' },
  { value: '09', label: 'Sep' },
  { value: '10', label: 'Oct' },
  { value: '11', label: 'Nov' },
  { value: '12', label: 'Dec' },
]

const selectClass =
  'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed bg-white'

export function MonthYearPicker({
  value,
  onChange,
  placeholder = 'Month',
  className = '',
  required,
  disabled,
  id,
}: MonthYearPickerProps) {
  const [month, year] = value ? value.split('/') : ['', '']

  const years = useMemo(() => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: 51 }, (_, i) => String(currentYear - 50 + i))
  }, [])

  const currentYear = years[years.length - 1]
  const displayYear = year || (value === '' ? currentYear : '')

  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMonth = e.target.value
    if (newMonth) {
      onChange(`${newMonth}/${displayYear}`)
    } else {
      onChange('')
    }
  }

  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newYear = e.target.value
    if (newYear) {
      onChange(`${month || '01'}/${newYear}`)
    } else {
      onChange('')
    }
  }

  return (
    <div className={`flex gap-2 ${className}`}>
      <select
        id={id ? `${id}-month` : undefined}
        value={month}
        onChange={handleMonthChange}
        required={required}
        disabled={disabled}
        className={selectClass}
        aria-label="Month"
      >
        <option value="">{placeholder}</option>
        {MONTHS.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
          </option>
        ))}
      </select>
      <select
        id={id ? `${id}-year` : undefined}
        value={displayYear}
        onChange={handleYearChange}
        required={required}
        disabled={disabled}
        className={selectClass}
        aria-label="Year"
      >
        <option value="">Year</option>
        {years.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </div>
  )
}
