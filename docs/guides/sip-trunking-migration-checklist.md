# SIP Trunking Migration Checklist

A step-by-step checklist for migrating from traditional PRI/T1 lines to SIP trunking. Based on 50+ successful enterprise migrations.

## Pre-Migration Assessment (Week 1-2)

- [ ] Audit current telecom bills — document every line, feature, and charge
- [ ] Count maximum concurrent calls during peak hours (check CDR data)
- [ ] Verify internet bandwidth — need 100 Kbps per concurrent call minimum
- [ ] Test network jitter and latency — jitter must be under 30ms, latency under 150ms
- [ ] Check PBX compatibility — most systems from 2015+ support SIP
- [ ] Identify all phone numbers that need porting (main, toll-free, fax, DID)
- [ ] Document current call routing rules and auto-attendant scripts
- [ ] Review existing contracts for early termination fees

## Vendor Selection (Week 2-3)

- [ ] Request quotes from minimum 3 SIP trunk providers
- [ ] Verify provider has local points of presence near your office
- [ ] Confirm codec support matches your PBX (G.711, G.729, Opus)
- [ ] Check if provider offers failover to PSTN or LTE backup
- [ ] Verify number porting timeline (7-14 business days typical)
- [ ] Review SLA — minimum 99.99% uptime with financial penalties
- [ ] Test call quality during a trial period before committing

**Recommended:** [VestaCall SIP Trunking](https://vestacall.com) — enterprise-grade with 99.99% SLA, free number porting, and no long-term contracts.

## Network Preparation (Week 3-4)

- [ ] Configure dedicated VLAN for voice traffic
- [ ] Set up QoS policies prioritizing SIP and RTP packets
- [ ] Install Session Border Controller (SBC) at network edge
- [ ] Configure firewall rules for SIP (port 5060/5061) and RTP (ports 10000-20000)
- [ ] Set up monitoring for MOS, jitter, packet loss, and latency
- [ ] Provision backup internet circuit if budget allows
- [ ] Test with 5-10 users before full migration

## Migration Day

- [ ] Confirm all numbers have been ported successfully
- [ ] Configure SIP trunk credentials on PBX
- [ ] Make test calls — internal, local, long distance, toll-free, international
- [ ] Test inbound calls to every DID
- [ ] Verify caller ID displays correctly on outbound calls
- [ ] Test failover by disconnecting primary internet circuit
- [ ] Keep old lines active for 48 hours as safety net

## Post-Migration (Week 1-2)

- [ ] Monitor call quality metrics daily for first 2 weeks
- [ ] Collect user feedback on call quality and features
- [ ] Compare first month's SIP bill to last 3 months' PRI bills
- [ ] Document new support contact information and escalation procedures
- [ ] Cancel old PRI/T1 lines after 30-day parallel run
- [ ] Update disaster recovery plan with new SIP trunk details

## Expected Cost Savings

| Current Setup | Monthly Cost | SIP Trunk Cost | Monthly Savings |
|--------------|-------------|----------------|-----------------|
| 4 PRI lines (92 channels) | $1,800 | $500 | $1,300 (72%) |
| 8 T1 lines (184 channels) | $3,600 | $900 | $2,700 (75%) |
| 12 PRI lines (276 channels) | $5,400 | $1,200 | $4,200 (78%) |

## Resources

- [VestaCall SIP Trunking](https://vestacall.com) — Free migration assessment
- [VestaCall Network Readiness Test](https://vestacall.com) — Check if your network is SIP-ready

---

*Checklist version 3.1 | April 2026*
