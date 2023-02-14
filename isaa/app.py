import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from numpy.random import randint
from flask import Flask, render_template, request

app = Flask(__name__)

# http://127.0.0.1:5001


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

# function for encoding the message


def encode_message(bits, bases, n):
    message = []
    for i in range(n):
        qc = QuantumCircuit(1, 1)
        if bases[i] == 0:  # Prepare qubit in Z-basis
            if bits[i] == 0:
                pass
            else:
                qc.x(0)
        else:  # Prepare qubit in X-basis
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        qc.barrier()
        message.append(qc)
    return message

# measure message


def measure_message(message, bases, n):
    backend = Aer.get_backend('aer_simulator')
    measurements = []
    for q in range(n):
        if bases[q] == 0:  # measuring in Z-basis
            message[q].measure(0, 0)
        if bases[q] == 1:  # measuring in X-basis
            message[q].h(0)
            message[q].measure(0, 0)
        aer_sim = Aer.get_backend('aer_simulator')
        qobj = assemble(message[q], shots=1, memory=True)
        result = aer_sim.run(qobj).result()
        measured_bit = int(result.get_memory()[0])
        measurements.append(measured_bit)
    return measurements

# remove garbage


def remove_garbage(a_bases, b_bases, bits, n):
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            # If both used the same basis, add
            # this to the list of 'good' bits
            good_bits.append(bits[q])
    return good_bits

# sample bits for output


def sample_bits(bits, selection):
    sample = []
    for i in selection:
        # use np.mod to make sure the
        # bit we sample is always in
        # the list range
        i = np.mod(i, len(bits))
        # pop(i) removes the element of the
        # list at index 'i'
        sample.append(bits.pop(i))
    return sample


@app.route("/result", methods=['POST', "GET"])
def result():
    output = request.form.to_dict()
    sender = output["sender"]
    receiver = output["receiver"]
    n = int(output["size"])
    n1 = int(output["size2"])
    msg = output["message"]
    eve = output["radio"]
    if (eve == "yes"):
        np.random.seed(seed=0)
        # Step 1
        # Alice generates bits
        alice_bits = randint(2, size=n)

        # Step 2
        # Create an array to tell us which qubits
        # are encoded in which bases
        alice_bases = randint(2, size=n)
        message = encode_message(alice_bits, alice_bases, n)

        # Interception!!
        eve_bases = randint(2, size=n)
        intercepted_message = measure_message(message, eve_bases, n)

        # Step 3
        # Decide which basis to measure in:
        bob_bases = randint(2, size=n)
        bob_results = measure_message(message, bob_bases, n)

        # Step 4
        alice_key = remove_garbage(alice_bases, bob_bases, alice_bits, n)
        bob_key = remove_garbage(alice_bases, bob_bases, bob_results, n)

        # Step 5
        sample_size = n1
        bit_selection = randint(n, size=sample_size)

        bob_sample = sample_bits(bob_key, bit_selection)
        bob = str(bob_sample)
        alice_sample = sample_bits(alice_key, bit_selection)
        alice = str(alice_sample)
        return render_template("index2.html", alice1=alice, bob1=bob, s=sender, r=receiver)
    else:
        np.random.seed(seed=0)
        # Step 1
        # Alice generates bits
        alice_bits = randint(2, size=n)

        # Step 2
        # Create an array to tell us which qubits
        # are encoded in which bases
        alice_bases = randint(2, size=n)
        message = encode_message(alice_bits, alice_bases, n)

        # Step 3
        # Decide which basis to measure in:
        bob_bases = randint(2, size=n)
        bob_results = measure_message(message, bob_bases, n)

        # Step 4
        alice_key = remove_garbage(alice_bases, bob_bases, alice_bits, n)
        bob_key = remove_garbage(alice_bases, bob_bases, bob_results, n)

        # Step 5
        sample_size = n1
        bit_selection = randint(n, size=sample_size)

        bob_sample = sample_bits(bob_key, bit_selection)
        bob = str(bob_sample)
        alice_sample = sample_bits(alice_key, bit_selection)
        alice = str(alice_sample)
        return render_template("index3.html", alice1=alice, bob1=bob, message=msg, s=sender, r=receiver)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
