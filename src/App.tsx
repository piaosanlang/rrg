import { useState, useEffect, useRef, useCallback } from "react";

const BENCHMARK = "SPY";
const TAIL_LENGTH = 12;

const QUADRANT_COLORS = {
  Leading: "#10b981",
  Weakening: "#f59e0b",
  Lagging: "#f43f5e",
  Improving: "#8b5cf6",
};

function getQuadrant(rs: number, mom: number) {
  if (rs >= 100 && mom >= 100) return "Leading";
  if (rs >= 100 && mom < 100) return "Weakening";
  if (rs < 100 && mom < 100) return "Lagging";
  return "Improving";
}

// ── Canvas helpers ──────────────────────────────────────────────
function drawArrowhead(
  ctx: CanvasRenderingContext2D,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  size: number,
  color: string
) {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  ctx.save();
  ctx.translate(x2, y2);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(-size, -size * 0.5);
  ctx.lineTo(-size, size * 0.5);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
  ctx.restore();
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

export default function RRGChart() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [rawData, setRawData] = useState<any[] | null>(null);
  const [data, setData] = useState<any[] | null>(null);
  const [hovered, setHovered] = useState<number | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [animFrame, setAnimFrame] = useState(TAIL_LENGTH - 1);
  const [playing, setPlaying] = useState(false);
  const frameRef = useRef(TAIL_LENGTH - 1);

  const W = 700,
    H = 590;
  const PAD = { top: 48, right: 48, bottom: 68, left: 68 };
  const CW = W - PAD.left - PAD.right;
  const CH = H - PAD.top - PAD.bottom;

  const [axisRange, setAxisRange] = useState({
    minRS: 93,
    maxRS: 108,
    minMom: 93,
    maxMom: 108,
  });

  const toX = useCallback(
    (rs: number) => PAD.left + ((rs - axisRange.minRS) / (axisRange.maxRS - axisRange.minRS)) * CW,
    [axisRange, CW]
  );

  const toY = useCallback(
    (mom: number) =>
      PAD.top + (1 - (mom - axisRange.minMom) / (axisRange.maxMom - axisRange.minMom)) * CH,
    [axisRange, CH]
  );

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}rrg-data.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => {
        setRawData(json);
      })
      .catch((err) => {
        console.error("Failed to load rrg-data.json.", err);
      });
  }, []);

  useEffect(() => {
    if (!rawData) return;

    setData(rawData);

    const allRS = rawData.flatMap((d: any) => d.trail.map((p: any) => p.rs));
    const allMom = rawData.flatMap((d: any) => d.trail.map((p: any) => p.mom));

    const pad = 2.0;
    setAxisRange({
      minRS: Math.floor(Math.min(...allRS) - pad),
      maxRS: Math.ceil(Math.max(...allRS) + pad),
      minMom: Math.floor(Math.min(...allMom) - pad),
      maxMom: Math.ceil(Math.max(...allMom) + pad),
    });

    const tailLen = rawData[0]?.trail?.length ?? TAIL_LENGTH;
    setAnimFrame(tailLen - 1);
    frameRef.current = tailLen - 1;
  }, [rawData]);

  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(() => {
      const next = frameRef.current + 1;
      if (!data) return;
      const maxFrame = data[0].trail.length - 1;

      if (next > maxFrame) {
        frameRef.current = maxFrame;
        setAnimFrame(maxFrame);
        setPlaying(false);
      } else {
        frameRef.current = next;
        setAnimFrame(next);
      }
    }, 480);

    return () => clearInterval(interval);
  }, [playing, data]);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;

    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = W + "px";
    canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const { minRS, maxRS, minMom, maxMom } = axisRange;

    ctx.fillStyle = "#080c18";
    ctx.fillRect(0, 0, W, H);

    const cx = toX(100),
      cy = toY(100);

    [
      {
        x: cx,
        y: PAD.top,
        w: W - PAD.right - cx,
        h: cy - PAD.top,
        c: "rgba(16,185,129,0.09)",
      },
      {
        x: cx,
        y: cy,
        w: W - PAD.right - cx,
        h: H - PAD.bottom - cy,
        c: "rgba(245,158,11,0.09)",
      },
      {
        x: PAD.left,
        y: cy,
        w: cx - PAD.left,
        h: H - PAD.bottom - cy,
        c: "rgba(244,63,94,0.09)",
      },
      {
        x: PAD.left,
        y: PAD.top,
        w: cx - PAD.left,
        h: cy - PAD.top,
        c: "rgba(139,92,246,0.09)",
      },
    ].forEach((f) => {
      ctx.fillStyle = f.c;
      ctx.fillRect(f.x, f.y, f.w, f.h);
    });

    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    ctx.lineWidth = 1;
    for (let v = minRS; v <= maxRS; v++) {
      ctx.beginPath();
      ctx.moveTo(toX(v), PAD.top);
      ctx.lineTo(toX(v), H - PAD.bottom);
      ctx.stroke();
    }
    for (let v = minMom; v <= maxMom; v++) {
      ctx.beginPath();
      ctx.moveTo(PAD.left, toY(v));
      ctx.lineTo(W - PAD.right, toY(v));
      ctx.stroke();
    }

    ctx.strokeStyle = "rgba(255,255,255,0.22)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 4]);

    ctx.beginPath();
    ctx.moveTo(cx, PAD.top);
    ctx.lineTo(cx, H - PAD.bottom);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(PAD.left, cy);
    ctx.lineTo(W - PAD.right, cy);
    ctx.stroke();

    ctx.setLineDash([]);

    [
      { t: "LEADING", x: W - PAD.right - 6, y: PAD.top + 16, a: "right", c: "#10b981" },
      { t: "WEAKENING", x: W - PAD.right - 6, y: H - PAD.bottom - 8, a: "right", c: "#f59e0b" },
      { t: "LAGGING", x: PAD.left + 6, y: H - PAD.bottom - 8, a: "left", c: "#f43f5e" },
      { t: "IMPROVING", x: PAD.left + 6, y: PAD.top + 16, a: "left", c: "#8b5cf6" },
    ].forEach((l) => {
      ctx.fillStyle = l.c + "88";
      ctx.font = "bold 10px 'Courier New', monospace";
      ctx.textAlign = l.a as CanvasTextAlign;
      ctx.fillText(l.t, l.x, l.y);
    });

    ctx.fillStyle = "rgba(255,255,255,0.35)";
    ctx.font = "10px 'Courier New', monospace";

    ctx.textAlign = "center";
    for (let v = minRS + 1; v < maxRS; v += 2) {
      ctx.fillText(v.toFixed(0), toX(v), H - PAD.bottom + 16);
    }

    ctx.textAlign = "right";
    for (let v = minMom + 1; v < maxMom; v += 2) {
      ctx.fillText(v.toFixed(0), PAD.left - 8, toY(v) + 4);
    }

    ctx.fillStyle = "rgba(255,255,255,0.45)";
    ctx.font = "11px 'Courier New', monospace";
    ctx.textAlign = "center";
    ctx.fillText("JdK RS-Ratio →", PAD.left + CW / 2, H - 10);

    ctx.save();
    ctx.translate(14, PAD.top + CH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("JdK RS-Momentum →", 0, 0);
    ctx.restore();

    const curDate = data[0]?.trail[Math.min(animFrame, data[0].trail.length - 1)]?.date || "";
    ctx.fillStyle = "rgba(0,212,255,0.7)";
    ctx.font = "bold 11px 'Courier New', monospace";
    ctx.textAlign = "right";
    ctx.fillText(`▸ ${curDate}`, W - PAD.right, PAD.top - 16);

    data.forEach((d, i) => {
      const isActive = hovered === i || selected === i;
      const visTrail = d.trail.slice(0, Math.min(animFrame + 1, d.trail.length));
      const n = visTrail.length;
      if (n < 1) return;

      for (let t = 0; t < n - 1; t++) {
        const p0 = visTrail[t],
          p1 = visTrail[t + 1];
        const progress = t / Math.max(n - 2, 1);
        const alpha = 0.12 + progress * 0.78;
        const lw = isActive ? 1.8 + progress * 4.5 : 0.8 + progress * 3;

        ctx.beginPath();
        ctx.moveTo(toX(p0.rs), toY(p0.mom));
        ctx.lineTo(toX(p1.rs), toY(p1.mom));
        ctx.strokeStyle = d.color + Math.round(alpha * 255).toString(16).padStart(2, "0");
        ctx.lineWidth = lw;
        ctx.lineCap = "round";
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(toX(p0.rs), toY(p0.mom), isActive ? 3 : 1.8, 0, Math.PI * 2);
        ctx.fillStyle =
          d.color + Math.round((0.15 + progress * 0.55) * 255).toString(16).padStart(2, "0");
        ctx.fill();
      }

      if (n >= 2) {
        const p0 = visTrail[n - 2],
          p1 = visTrail[n - 1];
        drawArrowhead(
          ctx,
          toX(p0.rs),
          toY(p0.mom),
          toX(p1.rs),
          toY(p1.mom),
          isActive ? 10 : 7,
          d.color + "dd"
        );
      }

      const cur = visTrail[n - 1];
      const x = toX(cur.rs),
        y = toY(cur.mom),
        r = isActive ? 11 : 8;

      const grd = ctx.createRadialGradient(x, y, r * 0.2, x, y, r * 3);
      grd.addColorStop(0, d.color + (isActive ? "55" : "28"));
      grd.addColorStop(1, d.color + "00");

      ctx.beginPath();
      ctx.arc(x, y, r * 3, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = d.color;
      ctx.fill();
      ctx.strokeStyle = "#080c18";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = isActive ? "#ffffff" : "rgba(255,255,255,0.8)";
      ctx.font = `${isActive ? "bold " : ""}10px 'Courier New', monospace`;
      ctx.textAlign = "center";
      ctx.fillText(d.ticker, x, y - r - 5);
    });

    const idx = selected !== null ? selected : hovered;
    if (idx !== null && data[idx]) {
      const d = data[idx];
      const cur = d.trail[Math.min(animFrame, d.trail.length - 1)];
      const x = toX(cur.rs),
        y = toY(cur.mom);
      const q = getQuadrant(cur.rs, cur.mom);

      let dirText = "";
      const fi = Math.min(animFrame, d.trail.length - 1);
      if (fi >= 1) {
        const prev = d.trail[fi - 1];
        const dr = cur.rs - prev.rs;
        const dm = cur.mom - prev.mom;
        dirText = `RS ${dr > 0.05 ? "↑" : dr < -0.05 ? "↓" : "→"}  MOM ${
          dm > 0.05 ? "↑" : dm < -0.05 ? "↓" : "→"
        }`;
      }

      const bw = 190,
        bh = dirText ? 100 : 82;
      const bx = Math.min(x + 14, W - bw - 10);
      const by = Math.max(Math.min(y - 14, H - bh - 10), PAD.top);

      ctx.fillStyle = "rgba(8,12,24,0.97)";
      ctx.strokeStyle = d.color;
      ctx.lineWidth = 1.5;
      roundRect(ctx, bx, by, bw, bh, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = d.color;
      ctx.font = "bold 11px 'Courier New', monospace";
      ctx.textAlign = "left";
      ctx.fillText(`${d.ticker}  ${d.name}`, bx + 10, by + 18);

      ctx.fillStyle = "rgba(255,255,255,0.62)";
      ctx.font = "10px 'Courier New', monospace";
      ctx.fillText(`RS-Ratio:    ${cur.rs.toFixed(2)}`, bx + 10, by + 35);
      ctx.fillText(`RS-Momentum: ${cur.mom.toFixed(2)}`, bx + 10, by + 50);

      ctx.fillStyle = QUADRANT_COLORS[q];
      ctx.font = "bold 11px 'Courier New', monospace";
      ctx.fillText(`▸ ${q}`, bx + 10, by + 67);

      if (dirText) {
        ctx.fillStyle = "rgba(255,255,255,0.42)";
        ctx.font = "10px 'Courier New', monospace";
        ctx.fillText(dirText, bx + 10, by + 83);
      }
    }
  }, [data, hovered, selected, animFrame, axisRange, toX, toY, CW, CH]);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!data || !canvasRef.current) return;
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let closest: number | null = null;
      let minD = 22;

      data.forEach((d, i) => {
        const cur = d.trail[Math.min(animFrame, d.trail.length - 1)];
        const dist = Math.hypot(mx - toX(cur.rs), my - toY(cur.mom));
        if (dist < minD) {
          minD = dist;
          closest = i;
        }
      });

      setHovered(closest);
    },
    [data, animFrame, toX, toY]
  );

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!data || !canvasRef.current) return;
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let closest: number | null = null;
      let minD = 22;

      data.forEach((d, i) => {
        const cur = d.trail[Math.min(animFrame, d.trail.length - 1)];
        const dist = Math.hypot(mx - toX(cur.rs), my - toY(cur.mom));
        if (dist < minD) {
          minD = dist;
          closest = i;
        }
      });

      setSelected((prev) => (prev === closest ? null : closest));
    },
    [data, animFrame, toX, toY]
  );

  const quadCounts = data
    ? ["Leading", "Weakening", "Lagging", "Improving"].reduce((acc: any, q) => {
        acc[q] = data.filter((d) => {
          const cur = d.trail[Math.min(animFrame, d.trail.length - 1)];
          return getQuadrant(cur.rs, cur.mom) === q;
        }).length;
        return acc;
      }, {})
    : {};

  const totalFrames = data ? data[0].trail.length - 1 : TAIL_LENGTH - 1;
  const frameDate = data
    ? data[0].trail[Math.min(animFrame, data[0].trail.length - 1)]?.date || ""
    : "";

  return (
    <div
      style={{
        background: "#080c18",
        minHeight: "100vh",
        fontFamily: "'Courier New', monospace",
        color: "#e2e8f0",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div style={{ width: "100%", maxWidth: 760, marginBottom: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div
              style={{
                fontSize: 22,
                fontWeight: "bold",
                letterSpacing: "0.1em",
                color: "#00d4ff",
              }}
            >
              ◈ RELATIVE ROTATION GRAPH
            </div>
            <div
              style={{
                fontSize: 11,
                color: "rgba(255,255,255,0.38)",
                marginTop: 4,
                letterSpacing: "0.05em",
              }}
            >
              BENCHMARK: {BENCHMARK} · WEEKLY · PYTHON-COMPUTED JDK-STYLE APPROXIMATION
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 10, color: "rgba(0,212,255,0.5)", marginBottom: 4 }}>
              LAST UPDATE
            </div>
            <div style={{ fontSize: 12, color: "#00d4ff", fontWeight: "bold" }}>{frameDate}</div>
          </div>
        </div>

        {data && (
          <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
            {Object.entries(quadCounts).map(([q, c]) => (
              <div
                key={q}
                style={{
                  background: QUADRANT_COLORS[q as keyof typeof QUADRANT_COLORS] + "18",
                  border: `1px solid ${
                    QUADRANT_COLORS[q as keyof typeof QUADRANT_COLORS]
                  }55`,
                  borderRadius: 4,
                  padding: "4px 12px",
                  fontSize: 11,
                  color: QUADRANT_COLORS[q as keyof typeof QUADRANT_COLORS],
                  letterSpacing: "0.06em",
                }}
              >
                {q.toUpperCase()} · {String(c)}
              </div>
            ))}
          </div>
        )}
      </div>

      <div
        style={{
          position: "relative",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 8,
          overflow: "hidden",
          boxShadow: "0 0 40px rgba(0,212,255,0.05)",
        }}
      >
        {!data && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(8,12,24,0.92)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 10,
              fontSize: 13,
              color: "#00d4ff",
              letterSpacing: "0.1em",
            }}
          >
            <span style={{ animation: "pulse 1s infinite" }}>LOADING RRG DATA...</span>
          </div>
        )}

        <canvas
          ref={canvasRef}
          style={{ display: "block", cursor: "crosshair" }}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHovered(null)}
          onClick={handleClick}
        />
      </div>

      {data && (
        <div
          style={{
            width: "100%",
            maxWidth: 700,
            marginTop: 12,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 6,
            padding: "12px 18px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <button
              onClick={() => {
                frameRef.current = 0;
                setAnimFrame(0);
                setPlaying(true);
              }}
              disabled={playing}
              style={{
                background: playing ? "rgba(0,212,255,0.08)" : "rgba(0,212,255,0.18)",
                border: "1px solid rgba(0,212,255,0.5)",
                color: "#00d4ff",
                padding: "5px 16px",
                borderRadius: 4,
                cursor: playing ? "default" : "pointer",
                fontSize: 11,
                letterSpacing: "0.08em",
                opacity: playing ? 0.5 : 1,
                whiteSpace: "nowrap",
              }}
            >
              {playing ? "▶ PLAYING..." : "▶ ANIMATE"}
            </button>

            <div style={{ flex: 1 }}>
              <input
                type="range"
                min={0}
                max={totalFrames}
                value={animFrame}
                onChange={(e) => {
                  const v = +e.target.value;
                  setAnimFrame(v);
                  frameRef.current = v;
                  setPlaying(false);
                }}
                style={{ width: "100%", accentColor: "#00d4ff", cursor: "pointer" }}
              />

              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 5 }}>
                {data[0].trail.map((p: any, i: number) => (
                  <span
                    key={i}
                    style={{
                      fontSize: 8,
                      color: i === animFrame ? "#00d4ff" : "rgba(255,255,255,0.2)",
                      fontWeight: i === animFrame ? "bold" : "normal",
                      letterSpacing: "0.01em",
                      transform: "rotate(-35deg)",
                      transformOrigin: "top center",
                      display: "block",
                      marginTop: 4,
                    }}
                  >
                    {p.date.slice(5)}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {data && (
        <div
          style={{
            width: "100%",
            maxWidth: 700,
            marginTop: 10,
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill,minmax(128px,1fr))",
            gap: 7,
          }}
        >
          {data.map((d, i) => {
            const cur = d.trail[Math.min(animFrame, d.trail.length - 1)];
            const q = getQuadrant(cur.rs, cur.mom);
            const active = selected === i || hovered === i;

            return (
              <div
                key={d.ticker}
                onClick={() => setSelected((prev) => (prev === i ? null : i))}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "5px 10px",
                  borderRadius: 4,
                  background: active ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.02)",
                  border: `1px solid ${active ? d.color + "66" : "rgba(255,255,255,0.07)"}`,
                  cursor: "pointer",
                  transition: "all 0.15s",
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: d.color,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <div style={{ fontSize: 11, fontWeight: "bold", color: d.color }}>{d.ticker}</div>
                  <div style={{ fontSize: 9, color: QUADRANT_COLORS[q as keyof typeof QUADRANT_COLORS] + "cc" }}>
                    {q}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div
        style={{
          width: "100%",
          maxWidth: 700,
          marginTop: 12,
          background: "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 6,
          padding: "12px 16px",
          fontSize: 11,
          color: "rgba(255,255,255,0.32)",
          lineHeight: 1.9,
        }}
      >
        <span style={{ color: "rgba(0,212,255,0.6)", fontWeight: "bold" }}>WEEKLY DATA · </span>
        Python-computed JdK-style approximation using Yahoo Finance daily closes aggregated into weekly closes.
        Tail = dynamic current week + last completed weeks ·{" "}
        <strong style={{ color: "rgba(255,255,255,0.45)" }}>dim→bright = old→recent</strong> ·
        arrowhead = direction of travel.{" "}
        <span style={{ color: "#10b981" }}>Leading</span> + arrow ↙ = rotating toward Weakening.{" "}
        <span style={{ color: "#8b5cf6" }}>Improving</span> + arrow ↗ = rotating toward Leading.
        Drag slider or hit <span style={{ color: "#00d4ff" }}>▶ ANIMATE</span> to replay.
      </div>

      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}`}</style>
    </div>
  );
}
