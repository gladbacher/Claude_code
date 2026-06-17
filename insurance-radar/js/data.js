// Sample insurance performance data
// scores: percentile rank within peer group (0-100), already inverted for "lower is better" metrics
// rawValues: actual measured values for display in tooltips and stat cards

const DATA = {
  broker: [
    {
      id: 'marsh',
      name: 'Marsh Commercial',
      meta: 'Global Broker · Commercial Lines',
      peerGroup: 'Top-tier brokers',
      scores: {
        hitRate: 72, quoteVolume: 96, gwpRetention: 85, policyRetention: 82,
        avgPremium: 88, lossRatio: 78, panelRank: 91, bindRate: 68,
        ntuRate: 74, claimsFreq: 71,
      },
      rawValues: {
        hitRate: 38.4, quoteVolume: 2840, gwpRetention: 91.2, policyRetention: 88.5,
        avgPremium: 6800, lossRatio: 58.3, panelRank: 2, bindRate: 52.1,
        ntuRate: 7.8, claimsFreq: 11.2,
      },
    },
    {
      id: 'aon',
      name: 'Aon Risk Solutions',
      meta: 'Global Broker · Multi-line',
      peerGroup: 'Top-tier brokers',
      scores: {
        hitRate: 65, quoteVolume: 99, gwpRetention: 88, policyRetention: 84,
        avgPremium: 92, lossRatio: 70, panelRank: 88, bindRate: 60,
        ntuRate: 68, claimsFreq: 66,
      },
      rawValues: {
        hitRate: 35.2, quoteVolume: 3420, gwpRetention: 92.8, policyRetention: 89.4,
        avgPremium: 7500, lossRatio: 62.1, panelRank: 3, bindRate: 47.5,
        ntuRate: 9.2, claimsFreq: 13.1,
      },
    },
    {
      id: 'wtwco',
      name: 'WTW Commercial',
      meta: 'Global Broker · Specialty Focus',
      peerGroup: 'Top-tier brokers',
      scores: {
        hitRate: 81, quoteVolume: 84, gwpRetention: 91, policyRetention: 89,
        avgPremium: 95, lossRatio: 85, panelRank: 94, bindRate: 77,
        ntuRate: 83, claimsFreq: 79,
      },
      rawValues: {
        hitRate: 42.7, quoteVolume: 1950, gwpRetention: 93.8, policyRetention: 91.2,
        avgPremium: 9200, lossRatio: 55.4, panelRank: 1, bindRate: 58.3,
        ntuRate: 6.1, claimsFreq: 9.4,
      },
    },
    {
      id: 'lockton',
      name: 'Lockton Companies',
      meta: 'Independent Broker · Private Clients',
      peerGroup: 'Top-tier brokers',
      scores: {
        hitRate: 88, quoteVolume: 71, gwpRetention: 93, policyRetention: 92,
        avgPremium: 82, lossRatio: 88, panelRank: 80, bindRate: 85,
        ntuRate: 90, claimsFreq: 84,
      },
      rawValues: {
        hitRate: 46.2, quoteVolume: 1320, gwpRetention: 94.5, policyRetention: 92.8,
        avgPremium: 5900, lossRatio: 53.8, panelRank: 4, bindRate: 63.4,
        ntuRate: 5.2, claimsFreq: 8.1,
      },
    },
    {
      id: 'gallagher',
      name: 'Gallagher',
      meta: 'Regional Broker · Growth Focus',
      peerGroup: 'Mid-tier brokers',
      scores: {
        hitRate: 58, quoteVolume: 78, gwpRetention: 76, policyRetention: 74,
        avgPremium: 61, lossRatio: 62, panelRank: 67, bindRate: 55,
        ntuRate: 60, claimsFreq: 57,
      },
      rawValues: {
        hitRate: 31.8, quoteVolume: 1680, gwpRetention: 87.4, policyRetention: 84.1,
        avgPremium: 3800, lossRatio: 66.9, panelRank: 8, bindRate: 43.2,
        ntuRate: 11.4, claimsFreq: 15.6,
      },
    },
    {
      id: 'howden',
      name: 'Howden Group',
      meta: 'Specialty Broker · Niche Lines',
      peerGroup: 'Mid-tier brokers',
      scores: {
        hitRate: 76, quoteVolume: 55, gwpRetention: 87, policyRetention: 85,
        avgPremium: 77, lossRatio: 80, panelRank: 72, bindRate: 71,
        ntuRate: 78, claimsFreq: 74,
      },
      rawValues: {
        hitRate: 40.1, quoteVolume: 920, gwpRetention: 92.1, policyRetention: 90.0,
        avgPremium: 5200, lossRatio: 57.1, panelRank: 6, bindRate: 54.8,
        ntuRate: 7.1, claimsFreq: 10.3,
      },
    },
    {
      id: 'bms',
      name: 'BMS Group',
      meta: 'Specialty Broker · London Market',
      peerGroup: 'Mid-tier brokers',
      scores: {
        hitRate: 69, quoteVolume: 48, gwpRetention: 79, policyRetention: 77,
        avgPremium: 98, lossRatio: 74, panelRank: 63, bindRate: 64,
        ntuRate: 71, claimsFreq: 68,
      },
      rawValues: {
        hitRate: 37.0, quoteVolume: 740, gwpRetention: 88.7, policyRetention: 85.9,
        avgPremium: 14500, lossRatio: 60.2, panelRank: 9, bindRate: 49.6,
        ntuRate: 8.8, claimsFreq: 12.4,
      },
    },
    {
      id: 'brunel',
      name: 'Brunel Professions',
      meta: 'Niche Broker · Professional Lines',
      peerGroup: 'Specialist brokers',
      scores: {
        hitRate: 94, quoteVolume: 32, gwpRetention: 95, policyRetention: 94,
        avgPremium: 70, lossRatio: 91, panelRank: 58, bindRate: 89,
        ntuRate: 95, claimsFreq: 90,
      },
      rawValues: {
        hitRate: 51.3, quoteVolume: 420, gwpRetention: 96.2, policyRetention: 94.8,
        avgPremium: 4600, lossRatio: 51.2, panelRank: 11, bindRate: 67.8,
        ntuRate: 3.8, claimsFreq: 6.9,
      },
    },
  ],

  segment: [
    {
      id: 'pi',
      name: 'Professional Indemnity',
      meta: 'Claims-made · Service industries',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 71, gwpGrowth: 78, policyGrowth: 72, hitRate: 74,
        policyRetention: 82, avgPremium: 88, claimsFreq: 76, profitability: 69,
      },
      rawValues: {
        lossRatio: 61.4, gwpGrowth: 8.2, policyGrowth: 6.4, hitRate: 39.2,
        policyRetention: 88.1, avgPremium: 3200, claimsFreq: 10.8, profitability: 14.2,
      },
    },
    {
      id: 'property',
      name: 'Commercial Property',
      meta: 'Material damage · Business interruption',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 58, gwpGrowth: 85, policyGrowth: 80, hitRate: 62,
        policyRetention: 78, avgPremium: 94, claimsFreq: 65, profitability: 54,
      },
      rawValues: {
        lossRatio: 67.8, gwpGrowth: 11.4, policyGrowth: 9.2, hitRate: 33.8,
        policyRetention: 85.4, avgPremium: 8700, claimsFreq: 14.2, profitability: 9.8,
      },
    },
    {
      id: 'liability',
      name: 'Liability',
      meta: 'Public & Employers Liability',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 82, gwpGrowth: 61, policyGrowth: 58, hitRate: 68,
        policyRetention: 85, avgPremium: 72, claimsFreq: 55, profitability: 78,
      },
      rawValues: {
        lossRatio: 55.1, gwpGrowth: 4.8, policyGrowth: 3.9, hitRate: 36.5,
        policyRetention: 89.6, avgPremium: 2100, claimsFreq: 16.9, profitability: 18.6,
      },
    },
    {
      id: 'motor',
      name: 'Motor Fleet',
      meta: 'Commercial vehicle · Fleet risk',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 44, gwpGrowth: 72, policyGrowth: 68, hitRate: 55,
        policyRetention: 91, avgPremium: 65, claimsFreq: 35, profitability: 40,
      },
      rawValues: {
        lossRatio: 74.2, gwpGrowth: 7.1, policyGrowth: 6.0, hitRate: 29.8,
        policyRetention: 92.4, avgPremium: 18500, claimsFreq: 28.4, profitability: 4.1,
      },
    },
    {
      id: 'cyber',
      name: 'Cyber & Technology',
      meta: 'First & third party · Tech E&O',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 61, gwpGrowth: 98, policyGrowth: 96, hitRate: 71,
        policyRetention: 70, avgPremium: 96, claimsFreq: 62, profitability: 58,
      },
      rawValues: {
        lossRatio: 64.3, gwpGrowth: 28.4, policyGrowth: 24.6, hitRate: 38.1,
        policyRetention: 82.3, avgPremium: 12400, claimsFreq: 15.1, profitability: 12.3,
      },
    },
    {
      id: 'marine',
      name: 'Marine & Cargo',
      meta: 'Hull · Cargo · Liability',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 74, gwpGrowth: 55, policyGrowth: 48, hitRate: 64,
        policyRetention: 76, avgPremium: 85, claimsFreq: 71, profitability: 72,
      },
      rawValues: {
        lossRatio: 59.8, gwpGrowth: 3.4, policyGrowth: 2.1, hitRate: 34.6,
        policyRetention: 84.8, avgPremium: 7600, claimsFreq: 11.4, profitability: 16.2,
      },
    },
    {
      id: 'construction',
      name: 'Construction & Engineering',
      meta: 'CAR · EAR · Professional risk',
      peerGroup: 'Commercial lines segments',
      scores: {
        lossRatio: 52, gwpGrowth: 81, policyGrowth: 75, hitRate: 58,
        policyRetention: 68, avgPremium: 91, claimsFreq: 48, profitability: 48,
      },
      rawValues: {
        lossRatio: 71.2, gwpGrowth: 10.1, policyGrowth: 8.3, hitRate: 31.4,
        policyRetention: 80.9, avgPremium: 22000, claimsFreq: 19.8, profitability: 7.6,
      },
    },
  ],

  product: [
    {
      id: 'pi-product',
      name: 'Professional Indemnity',
      meta: 'Claims-made · £1m–£10m limit',
      peerGroup: 'Commercial liability products',
      scores: {
        lossRatio: 74, combinedRatio: 72, gwpGrowth: 76, policyRetention: 83,
        claimsFreq: 78, avgClaimSize: 68, expenseRatio: 78, premiumAdequacy: 88,
      },
      rawValues: {
        lossRatio: 60.2, combinedRatio: 84.6, gwpGrowth: 8.4, policyRetention: 88.4,
        claimsFreq: 10.4, avgClaimSize: 48000, expenseRatio: 24.4, premiumAdequacy: 104,
      },
    },
    {
      id: 'el-product',
      name: "Employers' Liability",
      meta: 'Statutory · Bodily injury',
      peerGroup: 'Commercial liability products',
      scores: {
        lossRatio: 80, combinedRatio: 78, gwpGrowth: 52, policyRetention: 88,
        claimsFreq: 55, avgClaimSize: 44, expenseRatio: 85, premiumAdequacy: 76,
      },
      rawValues: {
        lossRatio: 56.8, combinedRatio: 80.4, gwpGrowth: 2.8, policyRetention: 90.8,
        claimsFreq: 17.2, avgClaimSize: 28000, expenseRatio: 23.6, premiumAdequacy: 98,
      },
    },
    {
      id: 'property-product',
      name: 'Commercial Property',
      meta: 'All risks · Material damage + BI',
      peerGroup: 'Property products',
      scores: {
        lossRatio: 58, combinedRatio: 55, gwpGrowth: 84, policyRetention: 79,
        claimsFreq: 64, avgClaimSize: 52, expenseRatio: 72, premiumAdequacy: 94,
      },
      rawValues: {
        lossRatio: 67.4, combinedRatio: 91.8, gwpGrowth: 11.8, policyRetention: 86.2,
        claimsFreq: 14.0, avgClaimSize: 65000, expenseRatio: 24.4, premiumAdequacy: 108,
      },
    },
    {
      id: 'motor-product',
      name: 'Motor Fleet',
      meta: 'Comprehensive · Commercial vehicles',
      peerGroup: 'Motor products',
      scores: {
        lossRatio: 42, combinedRatio: 38, gwpGrowth: 70, policyRetention: 92,
        claimsFreq: 34, avgClaimSize: 60, expenseRatio: 68, premiumAdequacy: 82,
      },
      rawValues: {
        lossRatio: 75.2, combinedRatio: 98.6, gwpGrowth: 7.4, policyRetention: 92.6,
        claimsFreq: 28.8, avgClaimSize: 5800, expenseRatio: 23.4, premiumAdequacy: 101,
      },
    },
    {
      id: 'cyber-product',
      name: 'Cyber Insurance',
      meta: 'First party · Third party · Tech E&O',
      peerGroup: 'Specialty products',
      scores: {
        lossRatio: 62, combinedRatio: 60, gwpGrowth: 98, policyRetention: 71,
        claimsFreq: 60, avgClaimSize: 38, expenseRatio: 58, premiumAdequacy: 78,
      },
      rawValues: {
        lossRatio: 64.8, combinedRatio: 88.2, gwpGrowth: 31.2, policyRetention: 82.6,
        claimsFreq: 15.8, avgClaimSize: 95000, expenseRatio: 23.4, premiumAdequacy: 99,
      },
    },
    {
      id: 'do-product',
      name: 'Management Liability (D&O)',
      meta: 'Directors & Officers · Side A/B/C',
      peerGroup: 'Specialty products',
      scores: {
        lossRatio: 85, combinedRatio: 83, gwpGrowth: 68, policyRetention: 86,
        claimsFreq: 82, avgClaimSize: 28, expenseRatio: 88, premiumAdequacy: 92,
      },
      rawValues: {
        lossRatio: 54.2, combinedRatio: 78.6, gwpGrowth: 6.8, policyRetention: 89.8,
        claimsFreq: 8.8, avgClaimSize: 180000, expenseRatio: 24.4, premiumAdequacy: 106,
      },
    },
  ],
};
