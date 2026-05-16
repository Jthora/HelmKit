//
//  AuraVoxelNode.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 10/22/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import SceneKit

enum AuraVoxelPhysicsCategory: Int {
    case linear
    case center
    case magnetic
}

enum AuraVoxelParticleImageType: Int {
    case square
    case hexagon
    case fuzz
    case spark
    case denseSpark
    case smoke
    case mix
}

class AuraVoxelNode:SCNNode {
    
    var readingDistance:CGFloat?
    var updateDelayTicks:Int = 0
    
    var mhdFieldNode:MagneticFieldNode
    var cellularConnectionNode:CellularConnectionNode
    var directionalFlowNode:DirectionalFlowNode
    var particleSystem: SCNParticleSystem
    //var fogParticleSystem: SCNParticleSystem
    
    static var lastParticleImageTypeForMixing:AuraVoxelParticleImageType = .square
    var particleImageType:AuraVoxelParticleImageType = .square {
        didSet {
            DispatchQueue.main.async {
                switch self.particleImageType {
                case .square: self.particleSystem.particleImage = nil
                case .hexagon: self.particleSystem.particleImage = UIImage(named: "Hexagon_64x")
                case .fuzz: self.particleSystem.particleImage = UIImage(named: "Fuzz_64x")
                case .spark: self.particleSystem.particleImage = UIImage(named: "Spark_64x")
                case .denseSpark: self.particleSystem.particleImage = UIImage(named: "Spark_Dense_64x")
                case .smoke: self.particleSystem.particleImage = UIImage(named: "Smoke_128x")
                case .mix:
                    switch AuraVoxelNode.lastParticleImageTypeForMixing {
                    case .square:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .hexagon
                        self.particleSystem.particleImage = UIImage(named: "Hexagon_64x")
                    case .hexagon:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .fuzz
                        self.particleSystem.particleImage = UIImage(named: "Fuzz_64x")
                    case .fuzz:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .spark
                        self.particleSystem.particleImage = UIImage(named: "Spark_64x")
                    case .spark:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .denseSpark
                        self.particleSystem.particleImage = UIImage(named: "Spark_Dense_64x")
                    case .denseSpark:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .smoke
                        self.particleSystem.particleImage = UIImage(named: "Smoke_128x")
                    case .smoke:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .square
                        self.particleSystem.particleImage = nil
                    default:
                        AuraVoxelNode.lastParticleImageTypeForMixing = .square
                        self.particleSystem.particleImage = nil
                    }
                }
            }
        }
    }
    
    var gameMode:Bool = false
    var gameSphere:GameSphereNode = GameSphereNode()
    
    var connection:CGFloat {
        set {
            self.cellularConnectionNode.signal = newValue
        }
        get {
            return self.cellularConnectionNode.signal
        }
    }
    
    var microTesla:CGFloat {
        set {
            self.mhdFieldNode.magnitude = newValue
        }
        get {
            return self.mhdFieldNode.magnitude
        }
    }
    
    var direction:SCNVector3 {
        set {
            self.directionalFlowNode.direction = newValue
        }
        get {
            return self.directionalFlowNode.direction
        }
    }
    
    static var blendmodeSwap:Bool = false
    init(connection:CGFloat = 0, microTesla:CGFloat = 0, direction:SCNVector3 = SCNVector3(0,0,0), subScale:CGFloat, gameMode:Bool = true) {
        cellularConnectionNode = CellularConnectionNode(signal: connection, subScale: subScale)
        mhdFieldNode = MagneticFieldNode(magnitude: microTesla, subScale: subScale)
        directionalFlowNode = DirectionalFlowNode(direction: direction, subScale: subScale)
        
        particleSystem = SCNParticleSystem(named: "FieldParticleSystem.scnp", inDirectory: nil)!
        particleSystem.emitterShape = SCNSphere(radius: subScale)
        particleSystem.isAffectedByGravity = true
        particleSystem.isAffectedByPhysicsFields = true
        
        if AuraVoxelNode.blendmodeSwap {
            particleSystem.blendMode = .additive
        } else {
            particleSystem.blendMode = .screen
        }
        AuraVoxelNode.blendmodeSwap = !AuraVoxelNode.blendmodeSwap
        
        particleSystem.particleColor = UIColor.init(red: 0.5, green: 1.0, blue: 0.5, alpha: 1)
        particleSystem.particleColorVariation = SCNVector4(1,1,1,0.5)
        particleSystem.particleAngleVariation = 360
        particleSystem.particleAngularVelocityVariation = 90
        particleSystem.particleCharge = 1
        particleSystem.particleMass = 1
        
        super.init()
        
        addParticleSystem(particleSystem)
        //addParticleSystem(fogParticleSystem)
        addChildNode(cellularConnectionNode)
        //addChildNode(mhdFieldNode)
        addChildNode(directionalFlowNode)
        
        if gameMode {
            addChildNode(gameSphere)
            self.gameMode = true
        }
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    func reset() {
        connection = 0
        microTesla = 0
        direction = SCNVector3(0,0,0)
        gameSphere.removeAllActions()
        gameSphere.removeFromParentNode()
        gameSphere = GameSphereNode()
        gameSphere.state = .new
        addChildNode(gameSphere)
        let lastParticleImageType = particleImageType
        particleImageType = lastParticleImageType
    }
    
    func enableDirectionalGravity() {
        directionalFlowNode.isActive = true
    }
    
    func disableDirectionalGravity() {
        directionalFlowNode.isActive = false
    }
    
    func enableRadialGravity() {
        cellularConnectionNode.isActive = true
    }
    
    func disableRadialGravity() {
        cellularConnectionNode.isActive = false
    }
    
    func calculateDirectionalFlow(right:AuraVoxelNode?, left:AuraVoxelNode?, up:AuraVoxelNode?, down:AuraVoxelNode?, front:AuraVoxelNode?, back:AuraVoxelNode?) {
        
        let r = (right?.connection ?? self.connection)
        let l = (left?.connection ?? self.connection)
        let u = (up?.connection ?? self.connection)
        let d = (down?.connection ?? self.connection)
        let f = (front?.connection ?? self.connection)
        let b = (back?.connection ?? self.connection)
        
        var dX = (r == 0 ? self.connection : r) - (l == 0 ? self.connection : l)
        var dY = (u == 0 ? self.connection : u) - (d == 0 ? self.connection : d)
        var dZ = (f == 0 ? self.connection : f) - (b == 0 ? self.connection : b)
        
        let maxVal = max(abs(dX),abs(dY),abs(dZ))
        
        guard maxVal > 0 else {
            direction = SCNVector3(0,0,0)
            return
        }
        
        dX = (dX/maxVal)
        dY = (dY/maxVal)
        dZ = (dZ/maxVal)
        
        direction = SCNVector3(dX,dY,dZ)
    }
}

class DirectionalFlowNode:SCNNode {
    
    var isActive:Bool = true {
        didSet {
            if isActive {
                self.physicsField?.isActive = true
            } else {
                self.physicsField?.isActive = false
            }
        }
    }
    
    var direction:SCNVector3 {
        set {
            self.physicsField!.direction = newValue
            if abs(newValue.x) + abs(newValue.y) + abs(newValue.z) > 0 {
                self.physicsField?.strength = 0.05
            } else {
                self.physicsField?.strength = 0
            }
        }
        get {
            return self.physicsField!.direction
        }
    }
    
    init(direction:SCNVector3, subScale:CGFloat) {
        
        super.init()
        
        let linearGravity = SCNPhysicsField.linearGravity()
        linearGravity.direction = direction
        linearGravity.minimumDistance = subScale*1.5
        linearGravity.halfExtent = SCNVector3(subScale*1.5,subScale*1.5,subScale*1.5)
        
        self.physicsField = linearGravity
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}


class MagneticFieldNode:SCNNode {
    
    var isActive:Bool = true {
        didSet {
            if isActive {
                self.physicsField?.isActive = true
            } else {
                self.physicsField?.isActive = false
            }
        }
    }
    
    var magnitude:CGFloat {
        set {
            self.physicsField!.strength = newValue
        }
        get {
            return self.physicsField!.strength
        }
    }
    
    init(magnitude:CGFloat, subScale:CGFloat) {
        
        super.init()
        
        self.physicsField = SCNPhysicsField.noiseField(smoothness: 0.5, animationSpeed: 1)
        self.physicsField?.minimumDistance = subScale
        self.physicsField?.halfExtent = SCNVector3(subScale,subScale,subScale)
        
        self.magnitude = magnitude
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
}


class CellularConnectionNode:SCNNode {
    
    
    var isActive:Bool = false {
        didSet {
            if isActive {
                self.physicsField?.isActive = true
            } else {
                self.physicsField?.isActive = false
            }
        }
    }
    
    var signal:CGFloat {
        set {
            let strength = newValue/50000
            if strength > 0.001 {
                self.physicsField!.strength = 0.001
            }
            self.physicsField!.strength = strength
        }
        get {
            return self.physicsField!.strength
        }
    }
    
    init(signal:CGFloat, subScale:CGFloat) {
        
        super.init()
        
        self.physicsField = SCNPhysicsField.radialGravity()
        self.physicsField?.minimumDistance = subScale/2
        self.physicsField?.halfExtent = SCNVector3(subScale/2,subScale/2,subScale/2)
        self.physicsField?.isActive = false
        self.signal = signal
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
}
