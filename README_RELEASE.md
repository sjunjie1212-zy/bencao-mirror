# BENCAO 3.6.4-AF3

Aroma Field hard rendering fix.

- 六味本草全部改为内联显式 RGBA 三层径向扩散。
- 不再依赖 color-mix、CSS RGB 自定义变量或伪元素承载核心色块。
- 色块强度按已确认视觉锁定：0.72 / 0.68 / 0.64 中心强度。
- 纸底加深至 #E7DFD2。
- CSS / JS cache key 更新至 364af3。
