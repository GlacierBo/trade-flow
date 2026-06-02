<script setup>
import wxQr from '../../pay/wx.png'
import zfbQr from '../../pay/zfb.png'
</script>

<template>
  <div class="max-w-lg mx-auto">
    <div class="bg-gray-800/50 rounded-2xl p-8 border border-gray-700/50 text-center">
      <!-- Header -->
      <div class="mb-8">
        <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-900/50 to-orange-900/50 border border-amber-700/50 flex items-center justify-center mx-auto mb-5">
          <svg class="w-10 h-10 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 8h1a4 4 0 1 1 0 8h-1"/>
            <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8z"/>
            <line x1="6" y1="2" x2="6" y2="4"/>
            <line x1="10" y1="2" x2="10" y2="4"/>
            <line x1="14" y1="2" x2="14" y2="4"/>
          </svg>
        </div>
        <h2 class="text-2xl font-black text-gray-100 mb-3">请作者喝杯咖啡</h2>
        <p class="text-sm text-gray-400 leading-relaxed max-w-sm mx-auto">
          如果这个小工具帮到了你，<br>欢迎请我喝杯咖啡
        </p>
        <p class="text-xs text-gray-500 mt-3">
          你的支持是我持续更新的动力
        </p>
      </div>

      <!-- QR Codes -->
      <div class="flex items-center justify-center gap-8 mb-8">
        <!-- WeChat -->
        <div class="flex flex-col items-center">
          <div class="qr-frame">
            <img :src="wxQr" alt="微信收款码" class="w-full h-full object-contain" />
          </div>
          <div class="flex items-center gap-1.5 mt-3">
            <svg class="w-4 h-4 text-green-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.713 4.516c-1.828-.052-3.786.477-5.322 1.71-1.96 1.597-2.864 4.027-2.162 6.37 1.04 3.456 5.438 5.27 8.855 4.072 2.833-.996 4.078-3.448 3.972-5.853-.812-.27-1.583-.636-2.306-1.082a.533.533 0 0 1-.213-.665l.39-1.48a.22.22 0 0 0-.048-.212.298.298 0 0 0-.29-.296c-.063 0-.13.027-.167.054l-1.903 1.114a.864.864 0 0 1-.717.098 8.3 8.3 0 0 1-.49-.092zm-1.545 2.046c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.983.97-.983zm4.844 0c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.983.97-.983z"/>
            </svg>
            <span class="text-sm font-bold text-gray-300">微信支付</span>
          </div>
        </div>

        <!-- Alipay -->
        <div class="flex flex-col items-center">
          <div class="qr-frame">
            <img :src="zfbQr" alt="支付宝收款码" class="w-full h-full object-contain" />
          </div>
          <div class="flex items-center gap-1.5 mt-3">
            <svg class="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M21.422 15.358c-.489-.18-3.455-1.244-4.285-1.571-.614 1.378-1.754 2.821-3.429 3.78 1.621.67 3.594.975 5.578.568 1.094-.225 2.37-.907 2.136-2.777zm-6.598-.569c.753-.376 1.405-.843 1.936-1.38-1.093-.55-2.377-.942-3.853-1.108.62 1.067 1.23 1.897 1.917 2.488zM13.63 6.838c-2.315-.004-4.392.646-5.98 1.687a11.278 11.278 0 0 0-1.573-.734c2.126-1.828 5.044-2.87 8.198-2.87 1.003 0 1.973.107 2.887.295C15.85 3.828 14.023 3 12 3 8.134 3 5 5.686 5 9c0 1.657.895 3.15 2.277 4.214a8.71 8.71 0 0 1-.296-.836C5.18 11.43 4 9.875 4 8.122v-.244C4 5.286 7.581 3 12 3c2.31 0 4.41.66 6.002 1.744a12.89 12.89 0 0 1 1.498.756 9.93 9.93 0 0 0-2.47-1.424c-1.557-.63-3.353-.97-5.19-.97-.163 0-.32.008-.477.014a12.854 12.854 0 0 1 2.278-.278z"/>
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
            </svg>
            <span class="text-sm font-bold text-gray-300">支付宝</span>
          </div>
        </div>
      </div>

      <!-- Disclaimer -->
      <div class="border-t border-gray-700/50 pt-5">
        <p class="text-xs text-gray-500 leading-relaxed">
          注：本页面属于纯自愿赞助，不解锁任何功能，不影响正常使用。
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.qr-frame {
  width: 160px;
  height: 160px;
  background: #1f2937;
  border: 2px solid #374151;
  border-radius: 16px;
  padding: 10px;
  transition: all 0.2s;
}

.qr-frame:hover {
  border-color: #4b5563;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
}
</style>
