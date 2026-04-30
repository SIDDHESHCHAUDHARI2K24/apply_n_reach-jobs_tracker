import ObservationPage from '../../../../src/app/job-tracker/ObservationPage'

interface Props {
  params: Promise<{ openingId: string }>
}

export default async function OpeningDetailRoutePage({ params }: Props) {
  const { openingId } = await params
  return <ObservationPage openingId={openingId} />
}
