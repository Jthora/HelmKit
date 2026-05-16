//
//  GameSphere.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 11/10/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import SceneKit

enum GameSphereNodeState: Int {
    case new
    case locking
    case updating
    case focused
    case locked
}

enum GameSphereNodeVisualMode: Int {
    case hidden
    case blue
    case bright
}

class GameSphereNode: SCNNode {
    
    var touched:Bool = false
    
    var newColor:UIColor = .blue
    var lockedColor:UIColor = .systemBlue
    
    var color:UIColor = UIColor.blue {
        didSet {
            self.geometry?.firstMaterial?.diffuse.contents = color
            self.geometry?.firstMaterial?.emission.contents = color
        }
    }
    
    var scaleOffset:CGFloat = 1
    func setScale(_ newScale:CGFloat) {
        scale = SCNVector3(newScale*scaleOffset,newScale*scaleOffset,newScale*scaleOffset)
    }
    
    var blendMode:SCNBlendMode {
        set {
            self.geometry?.firstMaterial?.blendMode = newValue
        }
        get {
            return self.geometry!.firstMaterial!.blendMode
        }
    }
    
    var mode:GameSphereNodeVisualMode = .blue {
        didSet {
            // Opacity animates and fades in for change
            
            switch mode {
            case .hidden:
                self.isHidden = true
                scaleOffset = 1
            case .blue:
                self.isHidden = false
                newColor = .systemBlue
                lockedColor = .blue
                scaleOffset = 1
            case .bright:
                self.isHidden = false
                newColor = .white
                lockedColor = .systemBlue
                scaleOffset = 1.2
            }
            
            let lastState = state
            self.state = lastState
        }
    }
    
    var state:GameSphereNodeState = .new {
        didSet {

            // Reset
            self.removeAllActions()
            
            switch state {
            case .new:
                
                self.blendMode = .screen
                self.color = newColor
                self.setScale(1)

                // 1st Half Animation
                let randomTimeOffset1 = TimeInterval.random
                let scaleUp = SCNAction.scale(by: 10/6, duration: 0.9+(randomTimeOffset1/10))
                let lightDown = SCNAction.fadeOpacity(to: 0.4, duration: 0.9+(randomTimeOffset1/10))
                scaleUp.timingMode = .easeInEaseOut;
                lightDown.timingMode = .easeInEaseOut;
                
                // 2st Half Animation
                let randomTimeOffset2 = TimeInterval.random
                let scaleDown = SCNAction.scale(by: 6/10, duration: 0.9+(randomTimeOffset2/10))
                let lightUp = SCNAction.fadeOpacity(to: 0.9, duration: 0.9+(randomTimeOffset2/10))
                scaleDown.timingMode = .easeInEaseOut;
                lightUp.timingMode = .easeInEaseOut;
                
                // Animation Loops
                let scaleSequence = SCNAction.sequence([scaleDown,scaleUp])
                let scaleLoop = SCNAction.repeatForever(scaleSequence)
                let lightSequence = SCNAction.sequence([lightUp,lightDown])
                let lightLoop = SCNAction.repeatForever(lightSequence)

                // Add Animation
                self.runAction(scaleLoop)
                self.runAction(lightLoop)
            
            case .updating:
                
                self.blendMode = .replace
                self.color = lockedColor
                self.setScale(1.2)

                // 1st Half Animation
                let randomTimeOffset1 = TimeInterval.random
                let scaleUp = SCNAction.scale(by: 10/8, duration: 0.2+(randomTimeOffset1/10))
                let lightDown = SCNAction.fadeOpacity(to: 0.7, duration: 0.2+(randomTimeOffset1/10))
                scaleUp.timingMode = .easeInEaseOut;
                lightDown.timingMode = .easeInEaseOut;
                
                // 2st Half Animation
                let randomTimeOffset2 = TimeInterval.random
                let scaleDown = SCNAction.scale(by: 8/10, duration: 0.2+(randomTimeOffset2/10))
                let lightUp = SCNAction.fadeOpacity(to: 1.0, duration: 0.2+(randomTimeOffset2/10))
                scaleDown.timingMode = .easeInEaseOut;
                lightUp.timingMode = .easeInEaseOut;
                
                // Animation Loops
                let scaleSequence = SCNAction.sequence([scaleDown,scaleUp])
                let scaleLoop = SCNAction.repeatForever(scaleSequence)
                let lightSequence = SCNAction.sequence([lightUp,lightDown])
                let lightLoop = SCNAction.repeatForever(lightSequence)

                // Add Animation
                self.runAction(scaleLoop)
                self.runAction(lightLoop)
            
            
            
            case .focused:
                
                self.blendMode = .add
                self.color = lockedColor
                self.setScale(1)

                // 1st Half Animation
                let randomTimeOffset1 = TimeInterval.random
                let scaleUp = SCNAction.scale(by: 10/8, duration: 0.4+(randomTimeOffset1/10))
                let lightDown = SCNAction.fadeOpacity(to: 0.5, duration: 0.4+(randomTimeOffset1/10))
                scaleUp.timingMode = .easeInEaseOut;
                lightDown.timingMode = .easeInEaseOut;
                
                // 2st Half Animation
                let randomTimeOffset2 = TimeInterval.random
                let scaleDown = SCNAction.scale(by: 8/10, duration: 0.4+(randomTimeOffset2/10))
                let lightUp = SCNAction.fadeOpacity(to: 0.9, duration: 0.4+(randomTimeOffset2/10))
                scaleDown.timingMode = .easeInEaseOut;
                lightUp.timingMode = .easeInEaseOut;
                
                // Animation Loops
                let scaleSequence = SCNAction.sequence([scaleDown,scaleUp])
                let scaleLoop = SCNAction.repeatForever(scaleSequence)
                let lightSequence = SCNAction.sequence([lightUp,lightDown])
                let lightLoop = SCNAction.repeatForever(lightSequence)

                // Add Animation
                self.runAction(scaleLoop)
                self.runAction(lightLoop)
                
            case .locking:
                
                self.blendMode = .add
                self.color = lockedColor
                self.setScale(1)
                
                self.removeAllActions()
                for node in self.childNodes {
                    node.removeFromParentNode()
                }
                
                let changeColor = SCNAction.customAction(duration: 1) { (node, elapsedTime) -> () in
                    let alpha = (1-(elapsedTime / 1))
                    self.color = self.lockedColor.withAlphaComponent(max(0.25,alpha*1.5))
                    
                    let scale = 1.2+((alpha-0.5)*3)
                    self.scale = SCNVector3(scale * self.scaleOffset,scale * self.scaleOffset,scale * self.scaleOffset)
                }
                self.runAction(changeColor) {
                    self.blendMode = .screen
                    self.state = .locked
                }
            case .locked:
                
                self.setScale(0.5)
                self.color = lockedColor.withAlphaComponent(0.25)
                self.blendMode = .screen
            }
        }
    }
    
    override init() {
        super.init()
        
        self.geometry = SCNSphere(radius: 0.01)
        self.mode = .blue
        self.state = .new
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
