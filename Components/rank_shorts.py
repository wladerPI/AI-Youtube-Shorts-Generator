from Components.ShortRanker import rank_shorts, export_results

OUTPUT_DIR = "output"

print("📊 Analisando retenção dos shorts...")

results = rank_shorts(OUTPUT_DIR)
export_results(results, OUTPUT_DIR)

print("🏆 Ranking finalizado.")
print(f"🔥 Shorts EXCELENTES: {len([r for r in results if r['class']=='EXCELENTE'])}")
