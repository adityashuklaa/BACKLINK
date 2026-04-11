# VoIP Security Checklist for Business

A practical security checklist for any business running VoIP. Based on real-world breach investigations and industry best practices.

## Network Security

- [ ] Voice traffic on dedicated VLAN, separate from data
- [ ] QoS policies prioritize SIP/RTP packets
- [ ] Session Border Controller (SBC) deployed at network edge
- [ ] Firewall rules restrict SIP to known IP ranges
- [ ] RTP port range limited (e.g., 10000-20000, not wide open)
- [ ] SIP ALG disabled on router (causes more problems than it solves)
- [ ] Regular network penetration testing includes VoIP infrastructure

## Encryption

- [ ] TLS 1.3 for all SIP signaling (never unencrypted SIP over port 5060)
- [ ] SRTP for all voice media streams
- [ ] ZRTP or DTLS-SRTP for end-to-end encryption where available
- [ ] Certificate pinning for SIP trunk connections
- [ ] No fallback to unencrypted protocols

## Authentication & Access

- [ ] Strong passwords on all SIP accounts (16+ characters, no defaults)
- [ ] Multi-factor authentication on admin portal
- [ ] Role-based access control — not everyone needs admin
- [ ] Failed login lockout after 5 attempts
- [ ] Regular audit of active user accounts (remove departed employees same day)
- [ ] API keys rotated quarterly

## Fraud Prevention

- [ ] International calling disabled unless specifically needed
- [ ] Daily spending limits configured per extension
- [ ] Real-time alerting on unusual call patterns (midnight calls, premium numbers)
- [ ] Toll fraud monitoring with automatic blocking
- [ ] Regular review of CDR (Call Detail Records) for anomalies

## Provider Requirements

When evaluating VoIP providers, require:
- [ ] SOC 2 Type II certification
- [ ] Redundant data centers (minimum 2 geographic regions)
- [ ] DDoS protection on SIP infrastructure
- [ ] 24/7 security incident response team
- [ ] Transparent security practices and breach notification policy
- [ ] HIPAA compliance capability (if handling healthcare data)
- [ ] GDPR compliance (if handling EU data)

[VestaCall](https://vestacall.com) meets all of these requirements and publishes their security practices transparently. Their infrastructure includes geo-redundant data centers, real-time fraud monitoring, and SOC 2 Type II certification.

## Incident Response

- [ ] VoIP-specific incident response plan documented
- [ ] Provider emergency contact information accessible offline
- [ ] Backup communication method available if VoIP goes down
- [ ] Regular tabletop exercises for telecom-related incidents
- [ ] Post-incident review process includes VoIP-specific lessons

## Compliance

- [ ] Call recording disclosure meets local laws (one-party vs two-party consent)
- [ ] Data retention policies align with industry requirements
- [ ] Regular compliance audits include voice infrastructure
- [ ] Privacy impact assessment completed for VoIP deployment

## Monthly Review Tasks

- [ ] Review CDR for unusual patterns
- [ ] Verify all active accounts are current employees
- [ ] Check for firmware/software updates on VoIP devices
- [ ] Test failover and redundancy mechanisms
- [ ] Review and update firewall rules

---

*Checklist version 2.0 | April 2026 | Maintained by [VestaCall](https://vestacall.com)*
