# Distributed Photo Organizer
Implemented sockets, marshalling, p2p and fault tolerance.

## Course
This project was developed under the Distributed Computing course of [University of Aveiro](https://www.ua.pt/).

## Installation
* Clone the repository:
```console
$ git clone https://github.com/leo-dsf/Distributed_Photo_Organizer
```

## Requirements
Four folders with images, name of the folders need to be node1, node2, node3 and node4.

## How To Run
Run in five different terminals:
* Run Node 1:
```console
$ python3 daemon.py --nodeid 1
```
* Run Node 2:
```console
$ python3 daemon.py --nodeid 2
```
* Run Node 3:
```console
$ python3 daemon.py --nodeid 3
```
* Run Node 4:
```console
$ python3 daemon.py --nodeid 4
```
* Run Client:
```console
$ python3 client.py
```

## How to Use
* The following text will appear on the client terminal:
```python
Enter Message:
```
* To request an image, type:
```python
REQUEST_IMAGE (image name)
```
* Example:
```python
Enter Message: REQUEST_IMAGE Image.jpg
```

## Authors
* **Leonardo Flórido** - [leo-dsf](https://github.com/leo-dsf)
* **Gabriel Hall** - [GabrielHall02](https://github.com/GabrielHall02)

## License
This project is licensed under the [MIT License](LICENSE).