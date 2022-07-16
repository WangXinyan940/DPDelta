# 实现计划

## 技术选择
本工作的目的是在这一类delta learning任务上实现一个通用工作流，技术选型偏向dflow。采样部分全部使用OpenMM及OpenMM-DeePMD插件；QM计算部分使用ORCA（noPBC），包含40个水，希望在dlpno-CCSD(T)/jun-cc-pvtz（如果可能），无法达到则使用double hybrid DFT/jun-cc-pvtz，再其次使用local-MP2/cc-pvtz。

## 工作流程

1. 训练
    - 使用已有数据训练若干DP模型
2. 验证
    - 使用验证数据表征模型质量
3. 采样
    - 使用给定的采样方式进行采样，或许可以使用平均模型？
4. 验证
    - 对于采样结果使用数个模型查验variance
5. 计算
    - 对于variance大的构象使用QM计算并加入训练集

## 实现计划

1. 实现采样部分的通用script
2. 实现QM训练的通用script
3. 实现数据规整的script
4. 实现DP训练的script
5. 实现DP验证的script
6. 将上述工作算符化，并实现工作流