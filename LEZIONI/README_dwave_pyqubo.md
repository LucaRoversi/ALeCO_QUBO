# Configurazione su Win10

Seguono i passi per creare un environment python in cui usare sia la libreria `pyqubo`, sia il D-Wave SDK ufficiale.

> conda install conda=24.1.2
> conda create --name dwave_pyqubo python=3.11
> conda activate dwave_pyqubo
> pip install pyqubo
> pip install dwave-ocean-sdk
> dwave auth login
> dwave auth get
> dwave config create --auto-token

genera:

> C:\Users\<user-name>\AppData\Local\dwavesystem\dwave-pyqubo

Dopodiché, selezionare l'interprete corretto, disponibile nell'environment `dwave_pyqubo':

> Ctrl-Shft-P > Python: Select interpreter > Python 3.11.8 ('dwave_pyqubo')

Infine, guardando [dwave-inspector](https://github.com/dwavesystems/dwave-inspector) installare librerie di proprietà D-Wave:

> pip install dwave-inspector
> pip install dwave-inspectorapp --extra-index-url=https://pypi.dwavesys.com/simple

## File di configurazione dwave.conf

Quello che uso ha struttura che ho ricavato dando un'occhiata anche a [D-Wave Ocean Software Documentation](https://docs.ocean.dwavesys.com/en/stable/docs_cli.html#)

> [defaults]
> token = DEV-......
>
> [default-solver]
> client = hybrid
> #solver = {"num_qubits__gt": 5000}
>
> #[hybrid]
> #client =
>
> [europe]
> region = eu-central-1
