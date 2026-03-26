import Link from "next/link";
import { MONEY_DEFAULTS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { getTranslations } from "next-intl/server";
import { buildMoneyHref } from "../query";
import type {
  MoneyCashNoteBand,
  MoneyChannel,
  MoneyQueryState,
} from "../types";

interface MoneyFiltersBarProps {
  instrumentCodes: string[];
  query: MoneyQueryState;
}

const CHANNELS: Array<{ value?: MoneyChannel; labelKey: string }> = [
  { value: undefined, labelKey: "money.allChannels" },
  { value: "counter", labelKey: "money.channelCounter" },
  { value: "non_cash", labelKey: "money.channelNonCash" },
  { value: "cash", labelKey: "money.channelCash" },
];

const ACTIONS = [
  { value: "buy", labelKey: "money.actionBuy" },
  { value: "sell", labelKey: "money.actionSell" },
] as const;

const NOTE_BANDS: Array<{ value?: MoneyCashNoteBand; labelKey: string }> = [
  { value: undefined, labelKey: "money.allNoteBands" },
  { value: "notes_50_500", labelKey: "money.noteBandLarge" },
  { value: "notes_1_20", labelKey: "money.noteBandSmall" },
];

function chipClassName(isActive: boolean): string {
  return cn(
    "border-[3px] border-neutral-950 px-4 py-3 text-xs font-black uppercase tracking-[0.14em]",
    isActive ? "bg-neutral-950 text-white" : "bg-white text-neutral-950",
  );
}

export async function MoneyFiltersBar({
  instrumentCodes,
  query,
}: MoneyFiltersBarProps) {
  const t = await getTranslations();
  const instruments = Array.from(
    new Set([query.instrumentCode, ...instrumentCodes.slice(0, MONEY_DEFAULTS.quickInstrumentLimit)]),
  );

  return (
    <div className="space-y-5">
      <div>
        <p className="mb-3 text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
          {t("money.instrument")}
        </p>
        <div className="flex flex-wrap gap-3">
          {instruments.map((instrumentCode) => (
            <Link
              key={instrumentCode}
              href={buildMoneyHref(
                {
                  instrumentCode,
                  historyOffset: 0,
                },
                query,
              )}
              scroll={false}
              className={chipClassName(query.instrumentCode === instrumentCode)}
            >
              {instrumentCode}
            </Link>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-3 text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
          {t("money.customerAction")}
        </p>
        <div className="flex flex-wrap gap-3">
          {ACTIONS.map((action) => (
            <Link
              key={action.value}
              href={buildMoneyHref(
                {
                  customerAction: action.value,
                  historyOffset: 0,
                },
                query,
              )}
              scroll={false}
              className={chipClassName(query.customerAction === action.value)}
            >
              {t(action.labelKey)}
            </Link>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-3 text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
          {t("money.channel")}
        </p>
        <div className="flex flex-wrap gap-3">
          {CHANNELS.map((channel) => (
            <Link
              key={channel.value ?? "all"}
              href={buildMoneyHref(
                {
                  channel: channel.value,
                  cashNoteBand: channel.value === "cash" ? query.cashNoteBand : undefined,
                  historyOffset: 0,
                },
                query,
              )}
              scroll={false}
              className={chipClassName((query.channel ?? undefined) === channel.value)}
            >
              {t(channel.labelKey)}
            </Link>
          ))}
        </div>
      </div>

      {query.channel === "cash" ? (
        <div>
          <p className="mb-3 text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
            {t("money.cashNoteBand")}
          </p>
          <div className="flex flex-wrap gap-3">
            {NOTE_BANDS.map((noteBand) => (
              <Link
                key={noteBand.value ?? "all"}
                href={buildMoneyHref(
                  {
                    cashNoteBand: noteBand.value,
                    historyOffset: 0,
                  },
                  query,
                )}
                scroll={false}
                className={chipClassName((query.cashNoteBand ?? undefined) === noteBand.value)}
              >
                {t(noteBand.labelKey)}
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
