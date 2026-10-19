import { useId } from "react";

const description = "The data version this answer used";

export function SnapshotId({ snapshot, asOf }: { snapshot: string; asOf?: string | null }) {
  const id = useId();
  // A visible tooltip on hover and keyboard focus, same pattern as RankedAnswer's route tips.
  return <span className="snapshot-wrap">
    <span className="snapshot" tabIndex={0} aria-describedby={id}>{asOf === undefined ? snapshot : asOf ? <>Data as of <time dateTime={asOf}>{asOf}</time></> : "Data date unavailable"}</span>
    <span className="snapshot-tip" role="tooltip" id={id}>{description}{asOf !== undefined && `: ${snapshot}`}</span>
  </span>;
}
