import { MoneyFeature } from "@/features/money";
import { getExchangeRates, getInflationRecords } from "@/services/money";

export default async function MoneyPage() {
  const [exchangeRates, inflationRecords] = await Promise.all([
    getExchangeRates(),
    getInflationRecords(),
  ]);

  return (
    <>
      <MoneyFeature exchangeRates={exchangeRates} inflationRecords={inflationRecords} />
    </>
  );
}
