/**
 * The ModelSpec mark 2a, inlined from brand/2a/modelspec-mark.svg without its
 * C2PA metadata block. Dark mode uses the transparent variant: the dark page
 * background is the tile colour, so the tile edge would not show anyway.
 */
export function BrandMark({
  transparent,
  size = 28,
}: {
  transparent: boolean;
  size?: number;
}) {
  const tile = "#0B1426";
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <rect id="tile" width="40" height="40" rx="3" fill={transparent ? "none" : tile} />
      <line
        id="y-axis"
        x1="6.5"
        y1="3"
        x2="6.5"
        y2="37.5"
        stroke="#F2C94C"
        strokeWidth="0.9"
        strokeLinecap="square"
      />
      <line
        id="x-axis"
        x1="3"
        y1="34"
        x2="37"
        y2="34"
        stroke="#3FB68B"
        strokeWidth="2.2"
        strokeLinecap="square"
      />
      <path
        id="m"
        d="M11 29L16 11L21 23L26 11L31 29"
        fill="none"
        stroke="#FFFFFF"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="miter"
      />
      <g
        id="dots"
        fill="#5AA9EC"
        stroke={transparent ? "none" : tile}
        strokeWidth="1"
      >
        {[
          [11, 29],
          [16, 11],
          [21, 23],
          [26, 11],
          [31, 29],
        ].map(([cx, cy]) => (
          <circle key={`${cx},${cy}`} cx={cx} cy={cy} r="1.9" />
        ))}
      </g>
    </svg>
  );
}
