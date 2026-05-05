import ObservationPage from '../../../../src/app/job-tracker/ObservationPage'

interface Props {
  params: Promise<{ openingId: string }>
}

export default async function JobOpeningDetailRoutePage({ params }: Props) {
  const { openingId } = await params
  return <ObservationPage openingId={openingId} />
}
