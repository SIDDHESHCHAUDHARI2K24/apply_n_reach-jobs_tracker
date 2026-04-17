import { IngestionPanel } from '@features/job-tracker/ingestion/IngestionPanel'
import { JobTrackerTable } from '@features/job-tracker/openings/JobTrackerTable'

export default function JobTrackerPage() {
  return (
    <div>
      <h1>Job Tracker</h1>
      <IngestionPanel />
      <JobTrackerTable />
    </div>
  )
}
