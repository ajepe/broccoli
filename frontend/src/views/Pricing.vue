<template>
  <div class="pricing-page">
    <div class="pricing-header">
      <h1>Simple, Transparent Pricing</h1>
      <p>Choose the perfect plan for your business</p>
    </div>

    <div class="pricing-toggle">
      <span :class="{ active: billing === 'monthly' }" @click="billing = 'monthly'">Monthly</span>
      <el-switch v-model="annual" />
      <span :class="{ active: billing === 'annual' }" @click="billing = 'annual'">
        Annual <small>(Save 20%)</small>
      </span>
    </div>

    <div class="pricing-cards">
      <div 
        v-for="plan in plans" 
        :key="plan.id"
        class="pricing-card"
        :class="{ featured: plan.featured }"
      >
        <div v-if="plan.featured" class="featured-badge">Most Popular</div>
        <h2>{{ plan.name }}</h2>
        <div class="price">
          <span class="currency">₦</span>
          <span class="amount">{{ annual ? plan.annualPrice : plan.price }}</span>
          <span class="period">/month</span>
        </div>
        <p class="description">{{ plan.description }}</p>
        
        <el-button 
          :type="plan.featured ? 'primary' : 'default'" 
          size="large" 
          @click="selectPlan(plan)"
        >
          Get Started
        </el-button>

        <ul class="features">
          <li v-for="feature in plan.features" :key="feature">
            <el-icon color="#67c23a"><Check /></el-icon>
            {{ feature }}
          </li>
        </ul>
      </div>
    </div>

    <div class="faq-section">
      <h2>Frequently Asked Questions</h2>
      <div class="faq-grid">
        <div class="faq-item">
          <h3>Can I upgrade my plan later?</h3>
          <p>Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
        </div>
        <div class="faq-item">
          <h3>Is my data backed up?</h3>
          <p>Yes, all plans include automated daily backups. Business and Enterprise plans include hourly backups.</p>
        </div>
        <div class="faq-item">
          <h3>Do you offer free trials?</h3>
          <p>Yes, we offer a 14-day free trial on all plans. No credit card required.</p>
        </div>
        <div class="faq-item">
          <h3>What payment methods do you accept?</h3>
          <p>We accept all major credit cards, PayPal, and bank transfers for annual plans.</p>
        </div>
      </div>
    </div>

    <div class="cta-section">
      <h2>Need a custom solution?</h2>
      <p>Contact us for custom Enterprise deployments</p>
      <div class="cta-buttons">
        <el-button type="primary" size="large">Contact Sales</el-button>
        <el-button size="large" @click="$router.push('/faq')">View FAQ</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const annual = ref(true)
const billing = ref('annual')

const plans = [
  {
    id: 'basic',
    name: 'Starter',
    price: 15000,
    annualPrice: 12000,
    description: 'Perfect for small businesses just getting started',
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
    price: 45000,
    annualPrice: 36000,
    description: 'Ideal for growing businesses with higher demands',
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
    price: 120000,
    annualPrice: 96000,
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
  background: #f5f7fa;
  padding: 40px 20px;
}

.pricing-header {
  text-align: center;
  margin-bottom: 40px;
}

.pricing-header h1 {
  font-size: 2.5rem;
  color: #303133;
  margin: 0;
}

.pricing-header p {
  font-size: 1.2rem;
  color: #909399;
  margin: 10px 0 0;
}

.pricing-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 40px;
}

.pricing-toggle span {
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
}

.pricing-toggle span.active {
  color: #303133;
  font-weight: bold;
}

.pricing-toggle small {
  color: #67c23a;
  font-size: 0.8rem;
}

.pricing-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.pricing-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px 30px;
  text-align: center;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.pricing-card.featured {
  border: 2px solid #00d9ff;
  transform: scale(1.05);
}

.pricing-card.featured:hover {
  transform: scale(1.05) translateY(-5px);
}

.featured-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #00d9ff;
  color: #fff;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.pricing-card h2 {
  color: #303133;
  margin: 0;
}

.price {
  margin: 20px 0;
}

.currency {
  font-size: 1.5rem;
  vertical-align: top;
}

.amount {
  font-size: 3.5rem;
  font-weight: bold;
  color: #303133;
}

.period {
  color: #909399;
}

.description {
  color: #909399;
  margin-bottom: 20px;
}

.features {
  list-style: none;
  padding: 0;
  margin-top: 30px;
  text-align: left;
}

.features li {
  padding: 8px 0;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 10px;
}

.faq-section {
  max-width: 1000px;
  margin: 80px auto;
}

.faq-section h2 {
  text-align: center;
  margin-bottom: 40px;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.faq-item {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.faq-item h3 {
  margin: 0 0 10px;
  color: #303133;
}

.faq-item p {
  margin: 0;
  color: #909399;
}

.cta-section {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 12px;
  max-width: 600px;
  margin: 40px auto;
}

.cta-section h2 {
  margin: 0;
}

.cta-section p {
  color: #909399;
  margin: 10px 0 20px;
}

@media (max-width: 900px) {
  .pricing-cards {
    grid-template-columns: 1fr;
  }
  
  .pricing-card.featured {
    transform: none;
  }
  
  .pricing-card.featured:hover {
    transform: translateY(-5px);
  }
  
  .faq-grid {
    grid-template-columns: 1fr;
  }
}
</style>
