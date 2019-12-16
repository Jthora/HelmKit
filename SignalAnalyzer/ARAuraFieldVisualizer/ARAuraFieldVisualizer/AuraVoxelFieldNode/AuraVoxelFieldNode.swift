//
//  AuraVoxelFieldNode.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 10/22/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import SceneKit
import CoreLocation


class AuraVoxelFieldNode:SCNNode {
    
    var referenceArray:[AuraVoxelNode] = []
    var voxelGrid:[Int:[Int:[Int:AuraVoxelNode]]] = [Int:[Int:[Int:AuraVoxelNode]]]()
    var divisions:Int
    var subScale:CGFloat
    
    // Used for sizing and gamification
    var averageConnection:CGFloat = 0
    var detectedPoints:Int = 0
    var totalPoints:Int {
        return referenceArray.count
    }
    
    var particleImageType:AuraVoxelParticleImageType {
        set {
            for node in referenceArray {
                node.particleImageType = newValue
            }
        }
        get {
            return referenceArray.first?.particleImageType ?? .square
        }
    }
    
    var isUsingDirectionalGravity:Bool = true {
        didSet {
            if isUsingDirectionalGravity {
                for node in referenceArray {
                    node.enableDirectionalGravity()
                }
            } else {
                for node in referenceArray {
                    node.disableDirectionalGravity()
                }
            }
        }
    }
    
    var isUsingRadialGravity:Bool = false {
        didSet {
            if isUsingRadialGravity {
                for node in referenceArray {
                    node.enableRadialGravity()
                }
            } else {
                for node in referenceArray {
                    node.disableRadialGravity()
                }
            }
        }
    }
    
    var gameMode:GameSphereNodeVisualMode = .blue {
        didSet {
            for node in referenceArray {
                node.gameSphere.mode = gameMode
            }
        }
    }
    
    private var _height:Int?
    var height:Int {
        get {
            return _height ?? divisions
        }
        set {
            _height = newValue
        }
    }
    
    init(divisions:Int, height:Int? = nil, subScale:CGFloat = 0.2) {
        self.divisions = divisions > 3 ? divisions : 3
        self._height = height != nil ? height! > 3 ? height : 3 : nil
        self.subScale = subScale
        super.init()
        setup()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    func setup(divisions:Int? = nil, subScale:CGFloat? = nil) {
        let divisions = divisions ?? self.divisions
        let subScale = subScale ?? self.subScale
        voxelGrid = [Int:[Int:[Int:AuraVoxelNode]]]()
        for x in -divisions ... divisions {
            voxelGrid[x] = [Int:[Int:AuraVoxelNode]]()
            for y in -height ... height {
                voxelGrid[x]![y] = [Int:AuraVoxelNode]()
                for z in -divisions ... divisions {
                    voxelGrid[x]![y]![z] = createAuraVoxelNode(x:x, y:y, z:z)
                    referenceArray.append(voxelGrid[x]![y]![z]!)
                    addChildNode(voxelGrid[x]![y]![z]!)
                }
            }
        }
    }
    
    func reset() {
        for node in referenceArray {
            node.reset()
        }
    }
    
    func createAuraVoxelNode(x:Int, y:Int, z:Int) -> AuraVoxelNode {
        let auraVoxelNode = AuraVoxelNode(subScale: subScale)
        auraVoxelNode.position = SCNVector3(CGFloat(x)*subScale,CGFloat(y)*subScale,CGFloat(z)*subScale)
        auraVoxelNode.gameSphere.state = .new
        return auraVoxelNode
    }
    
    func calculateDirectionalFlowField() {
        let dLimit = divisions - 2
        let hLimit = height - 2
        for x in -dLimit ... dLimit {
            for y in -hLimit ... hLimit {
                for z in -dLimit ... dLimit {
                    voxelGrid[x]![y]![z]!.calculateDirectionalFlow(right: (voxelGrid[x+1]![y]![z]!),
                                                            left: (voxelGrid[x-1]![y]![z]!),
                                                            above: (voxelGrid[x]![y+1]![z]!),
                                                            below: (voxelGrid[x]![y-1]![z]!),
                                                            front: (voxelGrid[x]![y]![z+1]!),
                                                            back: (voxelGrid[x]![y]![z-1]!))
                    
                }
            }
        }
    }
    
    func updateNodes(connection:CGFloat, microTesla:CGFloat, position: CLLocation, useAltitude:Bool = true) {
        let x = position.coordinate.longitude
        let y = useAltitude ? position.altitude : 0
        let z = position.coordinate.latitude
        let vectorPosition = SCNVector3(x,y,z) - self.position
        updateNodes(connection:connection, microTesla:microTesla, position: vectorPosition)
    }
    
    
    var lastUpdatedVoxel:AuraVoxelNode? = nil
    func updateNodes(connection:CGFloat, microTesla:CGFloat, position: SCNVector3) {
        let subScale = Float(self.subScale)
        let x = Int(((position.x / subScale) / scale.x).rounded())
        let y = Int(((position.y / subScale) / scale.y).rounded())
        let z = Int(((position.z / subScale) / scale.z).rounded())

        guard let thisVoxel = voxelGrid[x]?[y]?[z] else { return }
        
        var isUpdating:Bool = false

        let newReadingDistance = thisVoxel.gameSphere.position.distance(between: position)
        let lastReadingDistance = thisVoxel.readingDistance ?? newReadingDistance + 1
        
        if newReadingDistance < lastReadingDistance {
            isUpdating = true
            thisVoxel.readingDistance = newReadingDistance
        }
        
        if isUpdating {
            thisVoxel.connection = connection
            thisVoxel.microTesla = microTesla
            for iX in x-1 ... x+1 {
                for iY in y-1 ... y+1 {
                    for iZ in z-1 ... z+1 {
                        voxelGrid[iX]?[iY]?[iZ]?.calculateDirectionalFlow(right: (voxelGrid[iX+1]?[iY]?[iZ]),
                                                                        left: (voxelGrid[iX-1]?[iY]?[iZ]),
                                                                        above: (voxelGrid[iX]?[iY+1]?[iZ]),
                                                                        below: (voxelGrid[iX]?[iY-1]?[iZ]),
                                                                        front: (voxelGrid[iX]?[iY]?[iZ+1]),
                                                                        back: (voxelGrid[iX]?[iY]?[iZ-1]))
                    }
                }
            }
        }
        

        // Gamification
        DispatchQueue.main.async {
            
            switch thisVoxel.gameSphere.state {
            case .new:
                impact.impactOccurred()
                thisVoxel.gameSphere.state = .updating
            case .locked:
                if isUpdating {
                    thisVoxel.gameSphere.state = .updating
                } else {
                    thisVoxel.gameSphere.state = .focused
                }
            case .updating:
                if !isUpdating {
                    if thisVoxel.updateDelayTicks > 30 {
                        thisVoxel.gameSphere.state = .focused
                        thisVoxel.updateDelayTicks = 0
                    } else {
                        thisVoxel.updateDelayTicks += 1
                    }
                } else {
                    thisVoxel.updateDelayTicks = 0
                }
            case .focused:
                if isUpdating {
                    thisVoxel.gameSphere.state = .updating
                    thisVoxel.updateDelayTicks = 0
                }
            case .locking:
                break
            }
            
            if thisVoxel != self.lastUpdatedVoxel {
                self.lastUpdatedVoxel?.gameSphere.state = .locking
                thisVoxel.updateDelayTicks = 0
            }
            
            self.lastUpdatedVoxel = thisVoxel
        }
    }
}
