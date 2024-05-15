import SA

initialSolution =
solutionEvaluator =
initialTemp = 
finalTemp = 
tempReduction = "linear"
#tempReduction = "geometric"
#tempReduction = "slowDecrease"
# iterationPerTemp=100 # <--- default
neighborOperator =


sa = SA(initialSolution, solutionEvaluator, initialTemp, finalTemp, tempReduction, neighborOperator)
print(sa.run())