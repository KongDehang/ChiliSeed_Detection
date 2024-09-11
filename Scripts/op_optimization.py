"""
# 播种作业参数回归方程最值求解

"""

from sko.DE import DE


def _eq_optimize(seeding_rate):
    norm_value = (int(seeding_rate) - 800) / 200   # 实际值转为编码值

    # 优化目标函数（合格率）
    def _obj_func(p):
        x1, x2, x3 = p
        return -(97.37 + 0.53 * x1 - 0.98 * x2 - 0.47 * x3 - 0.45 * int(norm_value) - 1.5 * x2 * int(norm_value) -
                 1.43 * x1 ** 2 - 1.86 * x2 ** 2 - 2.33 * x3 ** 2 - 1.41 * int(norm_value) ** 2)

    # 约束条件
    constraint_ueq = [lambda x: 5 - (1.52 + 0.56 * x[0] - 0.86 * x[1] + 0.67 * x[2] - 0.47 * int(norm_value)),
                      lambda x: 1.52 + 0.56 * x[0] - 0.86 * x[1] + 0.67 * x[2] - 0.47 * int(norm_value),
                      # 0≤Y1≤5%  重播率

                      lambda x: 5 - (1.2 - 1.11 * x[0] + 1.68 * x[1] - 0.37 * x[2] + 0.92 * int(norm_value) + 0.8 *
                                     x[1] * int(norm_value) + 0.73 * x[2] * int(norm_value) + 1.25 * x[0] ** 2 + 2 * x[
                                         1]
                                     ** 2 + 1.74 * x[2] ** 2 + 1.69 * int(norm_value) ** 2),
                      lambda x: (1.2 - 1.11 * x[0] + 1.68 * x[1] - 0.37 * x[2] + 0.92 * int(norm_value) + 0.8 * x[
                          1] * int(norm_value) + 0.73 * x[2] * int(norm_value) + 1.25 * x[0] ** 2 + 2 * x[1]
                                 ** 2 + 1.74 * x[2] ** 2 + 1.69 * int(norm_value) ** 2),
                      # 0≤Y2≤5%  漏播率

                      lambda x: -90 - (
                                  97.37 + 0.53 * x[0] - 0.98 * x[1] - 0.47 * x[2] - 0.45 * int(norm_value) - 1.5 * x[
                              1] * int(norm_value) - 1.43 * x[0] ** 2 - 1.86 * x[1] ** 2 - 2.33 * x[
                                      2] ** 2 - 1.41 * int(
                              norm_value) ** 2),
                      lambda x: 100 - (
                                  97.37 + 0.53 * x[0] - 0.98 * x[1] - 0.47 * x[2] - 0.45 * int(norm_value) - 1.5 * x[
                              1] * int(norm_value) - 1.43 * x[0] ** 2 - 1.86 * x[1] ** 2 - 2.33 * x[
                                      2] ** 2 - 1.41 * int(
                              norm_value) ** 2)
                      # 90%≤Y3≤100%  合格率
                      ]
    de = DE(func=_obj_func, n_dim=3, size_pop=30, max_iter=30, lb=[-1, -1, -1], ub=[1, 1, 1],
            constraint_ueq=constraint_ueq)
    return de.run()


def get_result(seeding_rate=800):
    """
    获取优化结果
    :param seeding_rate: 当前作业速度（默认800盘/h）
    :return:
    """
    best_x, best_y = _eq_optimize(seeding_rate)

    # 编码值转实际值
    suc_pressure = best_x[0] * 2 + 13
    clr_pressure = best_x[1] + 2.5
    vib_frequency = best_x[2] * 5 + 35

    return [suc_pressure.round(1),
            clr_pressure.round(1),
            vib_frequency.round(1),
            -best_y[0].round(2)]


if __name__ == "__main__":
    res = get_result(600)
    res1 = get_result(800)
    res2 = get_result(1000)
    print(res, res1, res2)
