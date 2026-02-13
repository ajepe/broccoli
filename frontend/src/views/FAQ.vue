<template>
  <div class="faq-page">
    <div class="faq-header">
      <h1>Frequently Asked Questions</h1>
      <p>Everything you need to know about our Odoo hosting services</p>
    </div>

    <div class="faq-search">
      <el-input
        v-model="searchQuery"
        placeholder="Search for answers..."
        size="large"
        prefix-icon="Search"
        clearable
      />
    </div>

    <div class="faq-categories">
      <el-tabs v-model="activeCategory">
        <el-tab-pane label="General" name="general">
          <div class="faq-list">
            <el-collapse v-model="activeCollapse">
              <el-collapse-item title="What is Odoo Cloud Africa?" name="1">
                <div class="faq-content">
                  <p>Odoo Cloud Africa is a managed hosting platform specifically designed for businesses in Africa who want to use Odoo ERP. We provide isolated Docker containers with PostgreSQL databases, automated backups, SSL certificates, and 24/7 monitoring.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="How does the pricing work?" name="2">
                <div class="faq-content">
                  <p>We offer three plans:</p>
                  <ul>
                    <li><strong>Starter (₦15,000/mo)</strong> - 2GB RAM, daily backups, email support</li>
                    <li><strong>Business (₦45,000/mo)</strong> - 4GB RAM, hourly backups, Redis, priority support</li>
                    <li><strong>Enterprise (₦120,000/mo)</strong> - 8GB RAM, dedicated resources, 24/7 support</li>
                  </ul>
                  <p>All plans are billed monthly. Annual billing gets you 20% off.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Can I try before I buy?" name="3">
                <div class="faq-content">
                  <p>Yes! We offer a 14-day free trial on all plans. No credit card required. You get full access to all features during the trial period.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="What happens after I sign up?" name="4">
                <div class="faq-content">
                  <p>After signing up, your Odoo instance is automatically provisioned within minutes. You'll receive an email with:</p>
                  <ul>
                    <li>Your Odoo instance URL</li>
                    <li>Database credentials</li>
                    <li>Access to the admin panel</li>
                  </ul>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Is my data backed up?" name="5">
                <div class="faq-content">
                  <p>Absolutely! We take backups seriously:</p>
                  <ul>
                    <li><strong>Starter:</strong> Daily automated backups</li>
                    <li><strong>Business & Enterprise:</strong> Hourly automated backups</li>
                    <li>All backups are encrypted and stored in S3-compatible storage</li>
                    <li>Retention: 7 daily, 4 weekly, and 3 monthly backups</li>
                  </ul>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Technical" name="technical">
          <div class="faq-list">
            <el-collapse v-model="activeCollapse2">
              <el-collapse-item title="What versions of Odoo do you support?" name="t1">
                <div class="faq-content">
                  <p>We currently support Odoo 17 (latest stable). We also maintain images for Odoo 16 for customers who need to stay on older versions.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Can I install custom Odoo modules?" name="t2">
                <div class="faq-content">
                  <p>Yes! You have full access to your Odoo instance. You can:</p>
                  <ul>
                    <li>Install custom modules via the Apps menu</li>
                    <li>Upload custom modules directly</li>
                    <li>Access the server via SSH for advanced configuration</li>
                  </ul>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Do you provide SSL certificates?" name="t3">
                <div class="faq-content">
                  <p>Yes, all plans include free SSL certificates via Let's Encrypt. Certificates are automatically issued and renewed. Your site is accessible via HTTPS by default.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Can I use my own domain?" name="t4">
                <div class="faq-content">
                  <p>Yes! You can use your own domain. We'll provide you with the DNS records you need to point to your Odoo instance. Custom domains are included in Business and Enterprise plans.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Is Redis included?" name="t5">
                <div class="faq-content">
                  <p>Redis is included in Business and Enterprise plans. It significantly improves Odoo performance for production workloads. You can enable it from your control panel.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="What happens if I exceed my plan limits?" name="t6">
                <div class="faq-content">
                  <p>We'll notify you when you approach your limits. If you exceed them temporarily, we won't immediately suspend your service. However, for sustained overuse, we recommend upgrading your plan to ensure optimal performance.</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Billing" name="billing">
          <div class="faq-list">
            <el-collapse v-model="activeCollapse3">
              <el-collapse-item title="What payment methods do you accept?" name="b1">
                <div class="faq-content">
                  <p>We accept:</p>
                  <ul>
                    <li>Credit/Debit Cards (Visa, Mastercard, American Express)</li>
                    <li>PayPal</li>
                    <li>Bank Transfer (for annual plans)</li>
                    <li>Mobile Money (selected African countries)</li>
                  </ul>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Can I change my plan later?" name="b2">
                <div class="faq-content">
                  <p>Yes! You can upgrade or downgrade your plan at any time from your control panel. When upgrading, the new features are available immediately. When downgrading, changes take effect at the next billing cycle.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="What is your refund policy?" name="b3">
                <div class="faq-content">
                  <p>We offer a 30-day money-back guarantee for all plans. If you're not satisfied for any reason, contact us within 30 days for a full refund.</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="How do I cancel my subscription?" name="b4">
                <div class="faq-content">
                  <p>You can cancel anytime from your control panel. Your service will continue until the end of your billing period. You can export your data before cancellation.</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Support" name="support">
          <div class="faq-list">
            <el-collapse v-model="activeCollapse4">
              <el-collapse-item title="How do I get support?" name="s1">
                <div class="faq-content">
                  <p>We offer multiple support channels:</p>
                  <ul>
                    <li><strong>Email:</strong> support@odoocloud.africa</li>
                    <li><strong>Phone:</strong> Available on Business and Enterprise plans</li>
                    <li><strong>WhatsApp:</strong> Quick support via WhatsApp</li>
                    <li><strong>Tickets:</strong> 24/7 ticket system</li>
                  </ul>
                </div>
              </el-collapse-item>

              <el-collapse-item title="What are your support hours?" name="s2">
                <div class="faq-content">
                  <p>Support availability by plan:</p>
                  <ul>
                    <li><strong>Starter:</strong> Email support (business hours)</li>
                    <li><strong>Business:</strong> Priority email + phone (extended hours)</li>
                    <li><strong>Enterprise:</strong> 24/7 dedicated support</li>
                  </ul>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Do you offer migration services?" name="s3">
                <div class="faq-content">
                  <p>Yes! We offer free migration services for customers moving from other Odoo hosting providers. Our team will handle the entire migration process with zero downtime.</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="faq-cta">
      <h2>Still have questions?</h2>
      <p>Can't find the answer you're looking for? Our team is here to help.</p>
      <div class="cta-buttons">
        <el-button type="primary" size="large">Contact Support</el-button>
        <el-button size="large" @click="$router.push('/signup')">Get Started</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const searchQuery = ref('')
const activeCategory = ref('general')
const activeCollapse = ref(['1'])
const activeCollapse2 = ref(['t1'])
const activeCollapse3 = ref(['b1'])
const activeCollapse4 = ref(['s1'])
</script>

<style scoped>
.faq-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.faq-header {
  text-align: center;
  margin-bottom: 40px;
}

.faq-header h1 {
  font-size: 2.5rem;
  color: #303133;
  margin: 0;
}

.faq-header p {
  font-size: 1.2rem;
  color: #909399;
  margin: 10px 0 0;
}

.faq-search {
  max-width: 600px;
  margin: 0 auto 40px;
}

.faq-categories {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.faq-list {
  padding: 20px 0;
}

.faq-content {
  color: #606266;
  line-height: 1.8;
}

.faq-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.faq-content li {
  margin: 8px 0;
}

.faq-cta {
  text-align: center;
  margin-top: 60px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.faq-cta h2 {
  margin: 0;
  color: #303133;
}

.faq-cta p {
  color: #909399;
  margin: 10px 0 20px;
}

.cta-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}
</style>
