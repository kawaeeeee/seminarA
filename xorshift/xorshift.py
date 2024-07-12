import time

def compute_rand(results):
    random_number = 0
    for result in results:
        random_number = (random_number << 32) | result
    return random_number

def xorshift(seed):
    seed = seed ^ (seed << 13 & 0xFFFFFFFF)
    seed = seed ^ (seed >> 17 & 0xFFFFFFFF)
    seed = seed ^ (seed << 5 & 0xFFFFFFFF)
    return seed & 0xFFFFFFFF

def main():
    now_time = time.time()
    #print('Program start')

    results = []
    seeds = []

    for i in range(10):
        seeds.append(now_time + i)

    for seed in seeds:
        result_rand = int(seed)
        for i in range(10000000):
            result_rand = xorshift(result_rand)
        results.append(result_rand)
    

    # 結果を統合
    total_rand = compute_rand(results)
    print(f"Total Sum: {total_rand}")


    end_time = time.time()

    print(f"execution time {end_time - now_time}")

    # サーバー終了後の処理を続けるためのループ
    # while True:
    #     time.sleep(5)

if __name__ == '__main__':
    main()