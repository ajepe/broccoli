<template>
  <div class="payment-page">
    <el-card class="payment-card">
      <template #header>
        <div class="payment-header">
          <h2>Subscribe to {{ selectedPlan.name }} Plan</h2>
          <p>Complete your payment to activate your Odoo instance</p>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="Plan" />
        <el-step title="Payment" />
        <el-step title="Complete" />
      </el-steps>

      <div v-if="currentStep === 0" class="plan-summary">
        <div class="plan-details">
          <h3>{{ selectedPlan.name }} Plan</h3>
          <ul>
            <li v-for="feature in selectedPlan.features" :key="feature">✓ {{ feature }}</li>
          </ul>
          <div class="price-display">
            <span class="currency">₦</span>
            <span class="amount">{{ formatPrice(selectedPlan.price) }}</span>
            <span class="period">/month</span>
          </div>
        </div>

        <div class="billing-cycle">
          <el-radio-group v-model="billingCycle">
            <el-radio label="monthly">Monthly</el-radio>
            <el-radio label="annual">Annual (Save 20%)</el-radio>
          </el-radio-group>
        </div>

        <el-button type="primary" size="large" @click="proceedToPayment" class="full-width">
          Continue to Payment
        </el-button>
      </div>

      <div v-if="currentStep === 1" class="payment-form">
        <el-alert
          title="Secure Payment via Paystack"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          Your payment is secured by Paystack. We accept all Nigerian cards.
        </el-alert>

        <el-form :model="paymentForm" label-width="120px">
          <el-form-item label="Email">
            <el-input v-model="paymentForm.email" placeholder="Your email address" />
          </el-form-item>
          <el-form-item label="Phone">
            <el-input v-model="paymentForm.phone" placeholder="08012345678" />
          </el-form-item>
        </el-form>

        <div class="payment-summary">
          <div class="summary-row">
            <span>Plan</span>
            <span>{{ selectedPlan.name }}</span>
          </div>
          <div class="summary-row">
            <span>Billing</span>
            <span>{{ billingCycle }}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span>
            <span>₦{{ formatPrice(finalPrice) }}</span>
          </div>
        </div>

        <el-button 
          type="primary" 
          size="large" 
          :loading="processing" 
          @click="processPayment"
          class="full-width"
        >
          <el-icon><CreditCard /></el-icon>
          Pay ₦{{ formatPrice(finalPrice) }}
        </el-button>

        <div class="secure-badge">
          <el-icon><Lock /></el-icon>
          <span>Secured by Paystack</span>
        </div>
      </div>

      <div v-if="currentStep === 2" class="success-message">
        <el-result
          icon="success"
          title="Payment Successful!"
          sub-title="Your Odoo instance is being provisioned"
        >
          <template #extra>
            <el-button type="primary" @click="goToDashboard">Go to Dashboard</el-button>
          </template>
        </el-result>

        <div class="payment-details">
          <p><strong>Reference:</strong> {{ paymentReference }}</p>
          <p><strong>Amount:</strong> ₦{{ formatPrice(finalPrice) }}</p>
          <p>A confirmation email has been sent to {{ paymentForm.email }}</p>
        </div>
      </div>

      <div class="payment-footer">
        <el-button v-if="currentStep > 0 && currentStep < 2" @click="currentStep--">
          Back
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../stores/auth'

const router = useRouter()
const route = useRoute()

const currentStep = ref(0)
const processing = ref(false)
const billingCycle = ref('monthly')
const paymentReference = ref('')

const paymentForm = ref({
  email: '',
  phone: ''
})

const plans = {
  basic: {
    id: 'basic',
    name: 'Starter',
    price: 15000,
    features: ['2 GB RAM', '1 CPU Core', '10 GB Storage', 'Daily Backups', 'Email Support']
  },
  business: {
    id: 'business',
    name: 'Business',
    price: 45000,
    features: ['4 GB RAM', '2 CPU Cores', '25 GB Storage', 'Hourly Backups', 'Redis Cache', 'Priority Support']
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 120000,
    features: ['8 GB RAM', '4 CPU Cores', '100 GB Storage', 'Hourly Backups', 'Redis Cache', '24/7 Support', 'Custom Domain']
  }
}

const selectedPlan = computed(() => {
  const planId = route.query.plan || 'basic'
  return plans[planId] || plans.basic
})

const finalPrice = computed(() => {
  const price = selectedPlan.value.price
  if (billingCycle.value === 'annual') {
    return Math.round(price * 12 * 0.8)
  }
  return price
})

const formatPrice = (price) => {
  return price.toLocaleString()
}

const proceedToPayment = () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push({ path: '/login', query: { redirect: '/payment' } })
    return
  }
  currentStep.value = 1
}

const processPayment = async () => {
  if (!paymentForm.value.email) {
    ElMessage.warning('Please enter your email address')
    return
  }

  processing.value = true

  try {
    const response = await api.post('/payments/initialize', {
      plan: selectedPlan.value.id,
      billing_cycle: billingCycle.value
    })

    paymentReference.value = response.data.reference
    
    window.location.href = response.data.authorization_url
    
  } catch (error) {
    ElMessage.error('Failed to initialize payment')
    processing.value = false
  }
}

const goToDashboard = () => {
  router.push('/')
}

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    api.get('/clients').then(res => {
      if (res.data.length > 0) {
        paymentForm.value.email = res.data[0].email
      }
    })
  }
})
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

.payment-card {
  width: 500px;
  max-width: 100%;
}

.payment-header {
  text-align: center;
}

.payment-header h2 {
  margin: 0;
}

.payment-header p {
  color: #909399;
  margin: 5px 0 0;
}

.plan-summary {
  padding: 30px 0;
}

.plan-details {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.plan-details h3 {
  margin: 0 0 15px;
}

.plan-details ul {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}

.plan-details li {
  padding: 5px 0;
  color: #606266;
}

.price-display {
  text-align: center;
}

.price-display .currency {
  font-size: 1.5rem;
  vertical-align: top;
}

.price-display .amount {
  font-size: 3rem;
  font-weight: bold;
  color: #00d9ff;
}

.price-display .period {
  color: #909399;
}

.billing-cycle {
  text-align: center;
  margin-bottom: 20px;
}

.payment-form {
  padding: 20px 0;
}

.payment-summary {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-row.total {
  border-top: 1px solid #dcdfe6;
  font-weight: bold;
  font-size: 1.2rem;
  color: #00d9ff;
}

.full-width {
  width: 100%;
}

.secure-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 15px;
  color: #909399;
}

.success-message {
  text-align: center;
  padding: 20px 0;
}

.payment-details {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.payment-details p {
  margin: 8px 0;
}

.payment-footer {
  margin-top: 20px;
  text-align: center;
}
</style>
