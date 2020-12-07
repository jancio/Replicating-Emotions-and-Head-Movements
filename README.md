# Replicating Human Facial Emotions and Head Movements on a Robot Avatar

In this work, I propose a novel teleoperation system that combines the
replication of facial expressions of emotions (neutral, disgust, happiness, and surprise) and head movements on the fly on
the humanoid robot Nao. Robots’ expression of emotions is constrained by their physical and behavioural capabilities. As
the Nao robot has a static face, I use the LEDs located
around its eyes to reproduce the teleoperator expressions of
emotions. Using a web camera, I computationally detect
the facial action units and measure the head pose of the
operator. The emotion to be replicated is inferred from the
detected action units by a neural network. Simultaneously,
the measured head motion is smoothed and bounded to the
robot’s physical limits by applying a constrained-state Kalman
filter. In order to evaluate the proposed system, I conducted
a user study by asking 28 participants to use the replication
system by displaying facial expressions and head movements
while being recorded by a web camera. Subsequently, 18
external observers viewed the recorded clips via an online
survey and assessed the quality of the robot’s replication of the
participants’ behaviours. My results show that the proposed
teleoperation system can successfully communicate emotions
and head movements, resulting in a high agreement among
the external observers (ICCE = 0.91, ICCHP = 0.72).

This project was part of my [BA Thesis](https://github.com/jancio/Replicating-Emotions-and-Head-Movements/blob/master/Thesis/JanOndras_BA_Thesis_2017.pdf). It resulted in a **conference paper**:

> **Jan Ondras**, Oya Celiktutan, Evangelos Sariyanidi, and Hatice Gunes<br>
> [*Automatic replication of teleoperator head movements and facial expressions on a humanoid robot*](https://ieeexplore.ieee.org/abstract/document/8172386) <br>
> In 26th IEEE International Symposium on Robot and Human Interactive Communication (RO-MAN), 2017<br>
> Oral presentation

### Citation

	@article{Ondras2017AutomaticRO,
	  title={Automatic replication of teleoperator head movements and facial expressions on a humanoid robot},
	  author={Jan Ondras and Oya Çeliktutan and Evangelos Sariyanidi and Hatice Gunes},
	  journal={2017 26th IEEE International Symposium on Robot and Human Interactive Communication (RO-MAN)},
	  year={2017},
	  pages={745-750}
	}
