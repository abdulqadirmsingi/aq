import { MoneyFeature } from "@/features/money";
import { getExchangeRates, getInflationRecords } from "@/services/money";
import { getTranslations } from "next-intl/server";

export default async function MoneyPage() {
  const t = await getTranslations("money");
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
