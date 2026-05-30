import { ImageResponse } from '@vercel/og'

export const config = { runtime: 'edge' }

const BARS = 10
const SCORE = 0.74
const filled = Math.round(SCORE * BARS)

export default function handler() {
  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          width: '1200px',
          height: '630px',
          backgroundColor: '#1F3A2E',
          padding: '56px 64px',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '36px' }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '11px',
            border: '2px solid #FACC15',
            backgroundColor: 'rgba(250,204,21,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '22px',
          }}>🌿</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ color: 'white', fontSize: '26px', fontWeight: '900', letterSpacing: '-1px' }}>
              Claimify
            </span>
            <span style={{
              backgroundColor: '#FACC15', color: '#1F3A2E',
              fontSize: '11px', fontWeight: '800', letterSpacing: '2px',
              padding: '3px 9px', borderRadius: '999px',
            }}>ESG</span>
          </div>
          <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: '13px', marginLeft: '8px' }}>
            Greenwashing detection for oil &amp; gas majors
          </span>
        </div>

        {/* Claim card */}
        <div style={{
          flex: 1,
          backgroundColor: 'rgba(255,255,255,0.05)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '16px',
          padding: '36px 40px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}>
          {/* Company row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              backgroundColor: '#006DB7',
              borderRadius: '8px', width: '36px', height: '36px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'white', fontSize: '13px', fontWeight: '900', letterSpacing: '0.5px',
            }}>BP</div>
            <span style={{ color: 'rgba(255,255,255,0.45)', fontSize: '11px', fontWeight: '700', letterSpacing: '3px', textTransform: 'uppercase' }}>
              BP p.l.c · Emissions Reduction
            </span>
            <div style={{
              marginLeft: 'auto',
              backgroundColor: 'rgba(217,119,6,0.2)',
              border: '1px solid rgba(217,119,6,0.4)',
              color: '#FCD34D', fontSize: '11px', fontWeight: '700',
              padding: '4px 12px', borderRadius: '999px', letterSpacing: '0.5px',
            }}>
              weakly substantiated
            </div>
          </div>

          {/* Claim text */}
          <div style={{
            color: 'rgba(255,255,255,0.88)',
            fontSize: '21px',
            fontStyle: 'italic',
            lineHeight: '1.55',
            flex: 1,
          }}>
            "By 2030, we aim to reduce our net oil production by 40% and grow our
            low-carbon investment to $5bn per year — consistent with the goals of the
            Paris Agreement."
          </div>

          {/* GreenSignal row */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
              <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '12px', fontWeight: '600', letterSpacing: '1px' }}>
                GREENSIGNAL
              </span>
              <span style={{ color: '#F59E0B', fontSize: '38px', fontWeight: '900', fontFamily: 'monospace', letterSpacing: '-1px' }}>
                0.74
              </span>
            </div>
            {/* Score bar */}
            <div style={{ display: 'flex', gap: '4px' }}>
              {Array.from({ length: BARS }, (_, i) => (
                <div key={i} style={{
                  flex: 1, height: '7px', borderRadius: '99px',
                  backgroundColor: i < filled ? '#F59E0B' : 'rgba(255,255,255,0.08)',
                }} />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: '12px' }}>
            2,200+ claims scored · 10 oil &amp; gas majors
          </span>
          <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: '12px' }}>
            claimify-esg.vercel.app
          </span>
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
