<template>
  <div class="pricing-page">
    <div class="pricing-header">
      <div class="badge">Pricing</div>
      <h1>Simple, transparent pricing</h1>
      <p>Choose the perfect plan for your business needs. All plans include a 14-day free trial.</p>
      
      <div class="billing-toggle">
        <span :class="{ active: billing === 'monthly' }" @click="billing = 'monthly'">Monthly</span>
        <el-switch v-model="annual" />
        <span :class="{ active: billing === 'annual' }" @click="billing = 'annual'">
          Annual
          <span class="save-badge">Save 20%</span>
        </span>
      </div>
    </div>

    <div class="pricing-cards">
      <div 
        v-for="plan in plans" 
        :key="plan.id"
        class="pricing-card"
        :class="{ featured: plan.featured }"
      >
        <div v-if="plan.featured" class="popular-badge">Most Popular</div>
        
        <div class="plan-header">
          <h2>{{ plan.name }}</h2>
          <p>{{ plan.description }}</p>
        </div>
        
        <div class="plan-price">
          <span class="currency">₦</span>
          <span class="amount">{{ annual ? plan.annualPrice : plan.price }}</span>
          <span class="period">/month</span>
        </div>
        
        <el-button 
          :type="plan.featured ? 'primary' : 'default'" 
          size="large" 
          class="plan-btn"
          @click="selectPlan(plan)"
        >
          Get Started
        </el-button>
        
        <ul class="features">
          <li v-for="feature in plan.features" :key="feature">
            <el-icon class="check-icon"><Check /></el-icon>
            {{ feature }}
          </li>
        </ul>
      </div>
    </div>

    <div class="faq-section">
      <h2>Frequently Asked Questions</h2>
      <div class="faq-grid">
        <div class="faq-item">
          <h3>Can I change plans later?</h3>
          <p>Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately with prorated billing.</p>
        </div>
        <div class="faq-item">
          <h3>What's included in the free trial?</h3>
          <p>Full access to all features for 14 days. No credit card required to start your trial.</p>
        </div>
        <div class="faq-item">
          <h3>How do backups work?</h3>
          <p>Automatic daily backups for Starter plans, hourly for Business and Enterprise. All backups are encrypted and stored securely.</p>
        </div>
        <div class="faq-item">
          <h3>Do you offer support?</h3>
          <p>All plans include email support. Business and Enterprise plans get priority support with faster response times.</p>
        </div>
      </div>
    </div>

    <div class="cta-section">
      <div class="cta-content">
        <h2>Need a custom solution?</h2>
        <p>Contact us for custom Enterprise deployments with dedicated infrastructure</p>
        <el-button type="primary" size="large">Contact Sales</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const annual = ref(true)

const plans = [
  {
    id: 'basic',
    name: 'Starter',
    price: '15,000',
    annualPrice: '12,000',
    description: 'Perfect for small businesses getting started',
    featured: false,
    features: [
      '2 GB RAM',
      '1 CPU Core',
      '10 GB SSD Storage',
      '1 Database',
      'Daily Automated Backups',
      'Email Support',
      '99.9% Uptime SLA',
      'Basic Monitoring'
    ]
  },
  {
    id: 'business',
    name: 'Business',
    price: '45,000',
    annualPrice: '36,000',
    description: 'Ideal for growing businesses',
    featured: true,
    features: [
      '4 GB RAM',
      '2 CPU Cores',
      '25 GB SSD Storage',
      '1 Database',
      'Hourly Automated Backups',
      'Redis Cache',
      'Priority Support',
      '99.9% Uptime SLA',
      'Advanced Monitoring',
      'SSL Certificate'
    ]
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: '120,000',
    annualPrice: '96,000',
    description: 'Maximum performance for large organizations',
    featured: false,
    features: [
      '8 GB RAM',
      '4 CPU Cores',
      '100 GB SSD Storage',
      'Multiple Databases',
      'Hourly Automated Backups',
      'Redis Cache',
      '24/7 Dedicated Support',
      '99.99% Uptime SLA',
      'Advanced Monitoring',
      'Custom Domain',
      'White-label Options'
    ]
  }
]

const selectPlan = (plan) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    router.push({ path: '/payment', query: { plan: plan.id } })
  } else {
    router.push({ path: '/signup', query: { plan: plan.id } })
  }
}
</script>

<style scoped>
.pricing-page {
  min-height: 100vh;
  background: #F9FAFB;
  padding: 60px 20px;
}

.pricing-header {
  text-align: center;
  max-width: 600px;
  margin: 0 auto 60px;
}

.badge {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.pricing-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #111827;
  margin-bottom: 16px;
}

.pricing-header > p {
  font-size: 1.125rem;
  color: #6B7280;
  line-height: 1.7;
  margin-bottom: 32px;
}

.billing-toggle {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.billing-toggle span {
  font-weight: 500;
  color: #6B7280;
  cursor: pointer;
  transition: color 0.2s;
}

.billing-toggle span.active {
  color: #111827;
}

.save-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #10B981;
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-left: 8px;
}

.pricing-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto 80px;
}

.pricing-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  position: relative;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.pricing-card.featured {
  border-color: #6366F1;
  transform: scale(1.02);
}

.pricing-card.featured:hover {
  transform: scale(1.02) translateY(-4px);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  color: white;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.plan-header {
  margin-bottom: 24px;
}

.plan-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.plan-header p {
  color: #6B7280;
  font-size: 0.9rem;
}

.plan-price {
  margin-bottom: 24px;
}

.currency {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  vertical-align: top;
}

.amount {
  font-size: 3rem;
  font-weight: 800;
  color: #111827;
}

.period {
  color: #6B7280;
  font-size: 1rem;
}

.plan-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-weight: 600;
  margin-bottom: 32px;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.features li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  color: #4B5563;
  font-size: 0.9rem;
}

.check-icon {
  color: #10B981;
  font-weight: bold;
}

.faq-section {
  max-width: 900px;
  margin: 0 auto 60px;
}

.faq-section h2 {
  text-align: center;
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 40px;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.faq-item {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.faq-item h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.faq-item p {
  color: #6B7280;
  font-size: 0.9rem;
  line-height: 1.6;
}

.cta-section {
  max-width: 700px;
  margin: 0 auto;
}

.cta-content {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  border-radius: 20px;
  padding: 48px;
  text-align: center;
  color: white;
}

.cta-content h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.cta-content p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 24px;
}

@media (max-width: 900px) {
  .pricing-cards {
    grid-template-columns: 1fr;
    max-width: 400px;
  }
  
  .pricing-card.featured {
    transform: none;
  }
  
  .pricing-card.featured:hover {
    transform: translateY(-4px);
  }
  
  .faq-grid {
    grid-template-columns: 1fr;
  }
}
</style>
