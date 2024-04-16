import matplotlib.pyplot as plt
import numpy as npy
# Grafico
plt.figure()

# Punti che costituiscono l'insieme di addestramento.
punti = [(0, 3, '+'), (1, 3, '+'), (1, 2, '+'), (2, 1, '-'), (3, 1, '-'), (3, 2, '-'), (2, 2, '-')]
# I punti sono caratterizzati da un'etichetta scelta tra due.
# Gli insiemi di punti con la stessa etichetta sono gli insiemi di addestramento.

# Lo scopo è stabilire che etichetta assegnare ad un punto nuovo, che non è parte 
# dell'insieme dei punti di partenza, cioè di addestramento.
x_nuovo = 2.25
y_nuovo = 1.25
# Vettore che individua il nuovo punto da classificare
plt.quiver(0, 0, x_nuovo, y_nuovo, angles='xy', scale_units='xy', scale=1, color='tab:blue', width=0.003, label='nuovo')

# Rappresentazione dell'insieme di addestramento sul grafico.
# - raccolta delle coordinate dei punti di addestramento, con la stessa etichetta
x_pos = [x for x, y, label in punti if label == '+']
y_pos = [y for x, y, label in punti if label == '+']
x_neg = [x for x, y, label in punti if label == '-']
y_neg = [y for x, y, label in punti if label == '-']
# - punti sul grafico
plt.scatter(x_pos, y_pos, marker='+', color='b')
plt.scatter(x_neg, y_neg, marker='_', color='r')

# Vettori sul grafico
# for x, y, label in punti:
#     color = 'b' if label == '+' else 'r'
#     plt.quiver(0, 0, x, y, angles='xy', scale_units='xy', scale=1, color=color, width=0.001)

# 1mo passo verso la classificazione
# - punti medi relativi ai due insiemi di addestramento
media_x_pos = sum(x_pos)/len(x_pos)
media_y_pos = sum(y_pos)/len(y_pos)
media_x_neg = sum(x_neg)/len(x_neg)
media_y_neg = sum(y_neg)/len(y_neg)
# - punti medi sul grafico
plt.scatter(media_x_pos, media_y_pos, marker='*', color='g')
plt.scatter(media_x_neg, media_y_neg, marker='*', color='purple')
# - vettori medi sul grafico
# plt.quiver(0, 0, media_x_pos, media_y_pos, angles='xy', scale_units='xy', scale=1, color='g', width=0.002, label='media+')
# plt.quiver(0, 0, media_x_neg, media_y_neg, angles='xy', scale_units='xy', scale=1, color='purple', width=0.002, label='media-')

# 2do passo (non necessario) verso la classificazione
# - distanza tra i punti medi (centroidi?) dei due insiemi di addestramento
distanza_x_medie = (media_x_pos - media_x_neg)
distanza_y_medie = (media_y_pos - media_y_neg)
# - vettore tra i centroidi 
plt.quiver(media_x_neg, media_y_neg, distanza_x_medie, distanza_y_medie, angles='xy', scale_units='xy', scale=1, color='k', width=0.003, label='dist.')

# 3zo passo verso la classificazione
# - distanza media tra i centroidi
meta_distanza_x = (media_x_pos + media_x_neg)/2
meta_distanza_y = (media_y_pos + media_y_neg)/2
# - distanza media tra i centroidi sul grafico 
plt.scatter(meta_distanza_x, meta_distanza_y, marker='*', color='tab:orange')

# 4to passo verso la classificazione 
# - distanza del nuovo punto dalla distanza media tra i due centroidi
distanza_x_nuovo = x_nuovo - meta_distanza_x
distanza_y_nuovo = y_nuovo - meta_distanza_y
# - vettore sul grafico 
plt.quiver(meta_distanza_x, meta_distanza_y, distanza_x_nuovo, distanza_y_nuovo, angles='xy', scale_units='xy', scale=1, color='tab:orange', width=0.003, label='nuovo-dist.')


# 5to passo verso la classificazione
# - dot product tra il nuovo punto e e il punto medio tra i centroidi
dot_product = distanza_x_nuovo * distanza_x_medie + distanza_y_nuovo * distanza_y_medie
# - segno del dot product
sign_dot_product = npy.sign(dot_product)
# - assegna etichetta in base al segno
plt.scatter(x_nuovo, y_nuovo, marker='+' if sign_dot_product >= 0 else '_', color='b' if sign_dot_product >= 0 else 'r')


# Mostra grafico con legenda
plt.legend(loc='upper right')
plt.show()
